
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

// ====================
// Small utils
// ====================
export function setText(el, text) {
    if (!el) return;
    el.textContent = text;
}

export function fmtV(v) {
    return `{ x:${v.x.toFixed(3)}, y:${v.y.toFixed(3)}, z:${v.z.toFixed(3)} }`;
}

export function clampDt(dt) {
    return Math.min(0.05, Math.max(0, dt));
}

// ====================
// Logging
// ====================
export function createLogger({ hudRight, maxLines = 30 } = {}) {
    const logLines = [];
    function ts() {
        const d = new Date();
        const ms = String(d.getMilliseconds()).padStart(3, "0");
        return `${d.toLocaleTimeString()}.${ms}`;
    }
    function log(msg) {
        const line = `[${ts()}] ${msg}`;
        console.log(line);
        logLines.push(line);
        if (logLines.length > maxLines) logLines.shift();
        if (hudRight) hudRight.textContent = logLines.join("\n");
    }
    return {
        log,
        ts,
        getLines: () => logLines.slice(),
        clear: () => {
            logLines.length = 0;
            if (hudRight) hudRight.textContent = "";
        },
    };
}

// ====================
// CCD IK
// ====================
export function makeCCDSolver() {
    const effPos = new THREE.Vector3();
    const bonePos = new THREE.Vector3();
    const v1 = new THREE.Vector3();
    const v2 = new THREE.Vector3();
    const axis = new THREE.Vector3();

    const parentWorldQ = new THREE.Quaternion();
    const qWorld = new THREE.Quaternion();
    const qLocal = new THREE.Quaternion();

    return function solveCCD(chain, effector, targetWorld, {
        iters = 18,
        threshold = 0.012,
        maxStep = Math.PI / 18
    } = {}) {
        let earlyExit = false;

        for (let iter = 0; iter < iters; iter++) {
            effector.updateWorldMatrix(true, false);
            effector.getWorldPosition(effPos);

            const dist = effPos.distanceTo(targetWorld);
            if (dist < threshold) {
                earlyExit = true;
                break;
            }

            for (let i = 0; i < chain.length; i++) {
                const bone = chain[i];
                bone.updateWorldMatrix(true, false);

                bone.getWorldPosition(bonePos);
                effector.getWorldPosition(effPos);

                v1.copy(effPos).sub(bonePos).normalize();
                v2.copy(targetWorld).sub(bonePos).normalize();

                let dot = THREE.MathUtils.clamp(v1.dot(v2), -1, 1);
                let ang = Math.acos(dot);
                if (!isFinite(ang) || ang < 1e-6) continue;
                ang = Math.min(ang, maxStep);

                axis.copy(v1).cross(v2);
                if (axis.lengthSq() < 1e-12) continue;
                axis.normalize();

                qWorld.setFromAxisAngle(axis, ang);

                const parent = bone.parent;
                if (parent) parent.getWorldQuaternion(parentWorldQ);
                else parentWorldQ.identity();

                qLocal.copy(parentWorldQ).invert().multiply(qWorld).multiply(parentWorldQ);
                bone.quaternion.premultiply(qLocal);
                bone.updateMatrixWorld(true);
            }
        }

        effector.getWorldPosition(effPos);
        return { effPos: effPos.clone(), earlyExit };
    };
}

// ====================
// Preserve world transform while re-parenting under a bone.
// ====================
const _attachChildWorldM = new THREE.Matrix4();
const _attachParentWorldInvM = new THREE.Matrix4();
const _attachLocalM = new THREE.Matrix4();

export function reparentPreserveWorld(child, newParent) {
    if (!child || !newParent) return;

    child.updateWorldMatrix(true, false);
    newParent.updateWorldMatrix(true, false);

    _attachChildWorldM.copy(child.matrixWorld);
    _attachParentWorldInvM.copy(newParent.matrixWorld).invert();
    _attachLocalM.multiplyMatrices(_attachParentWorldInvM, _attachChildWorldM);

    newParent.add(child);
    child.matrix.copy(_attachLocalM);
    child.matrix.decompose(child.position, child.quaternion, child.scale);
    child.updateMatrixWorld(true);
}

// ====================
// Wrist orientation constraint
// ====================
export function createHandOrientationConstraintApplier({
    defaultFingerDirLocal = new THREE.Vector3(0, 1, 0),
    defaultPalmNormalLocal = new THREE.Vector3(-1, 0, 1),
} = {}) {
    const _qParentW = new THREE.Quaternion();
    const _qWorld = new THREE.Quaternion();
    const _qLocal = new THREE.Quaternion();

    function applyWorldAxisRotationToBone(bone, axisWorld, angleRad) {
        const parent = bone.parent;
        if (parent) parent.getWorldQuaternion(_qParentW);
        else _qParentW.identity();

        _qWorld.setFromAxisAngle(axisWorld, angleRad);
        _qLocal.copy(_qParentW).invert().multiply(_qWorld).multiply(_qParentW);

        bone.quaternion.premultiply(_qLocal);
        bone.updateMatrixWorld(true);
    }

    const _handWQ = new THREE.Quaternion();
    const _curFingerW = new THREE.Vector3();
    const _curPalmW = new THREE.Vector3();
    const _desFingerW = new THREE.Vector3();
    const _desPalmW = new THREE.Vector3();
    const _axisW = new THREE.Vector3();
    const _tmpA = new THREE.Vector3();
    const _tmpB = new THREE.Vector3();
    const _tmpC = new THREE.Vector3();

    function applyHandOrientationConstraint({
        handBone,
        forearmBone,
        desiredFingerDirWorld,
        desiredPalmNormalWorld,
        dt,
        strength = 12.0,
    }) {
        if (!handBone || !forearmBone) return;

        const alpha = 1.0 - Math.exp(-dt * strength);

        handBone.getWorldQuaternion(_handWQ);

        const fingerLocal = _tmpA.copy(defaultFingerDirLocal).normalize();
        const palmLocal = _tmpB.copy(defaultPalmNormalLocal).normalize();

        _curFingerW.copy(fingerLocal).applyQuaternion(_handWQ).normalize();
        _curPalmW.copy(palmLocal).applyQuaternion(_handWQ).normalize();

        _desFingerW.copy(desiredFingerDirWorld).normalize();
        _desPalmW.copy(desiredPalmNormalWorld).normalize();

        // 1) align finger dir
        _axisW.copy(_curFingerW).cross(_desFingerW);
        if (_axisW.lengthSq() > 1e-10) {
            _axisW.normalize();
            const dot = THREE.MathUtils.clamp(_curFingerW.dot(_desFingerW), -1, 1);
            const fullAngle = Math.acos(dot);
            applyWorldAxisRotationToBone(handBone, _axisW, fullAngle * alpha);
        }

        // 2) twist around finger axis to align palm normal
        handBone.getWorldQuaternion(_handWQ);
        _curPalmW.copy(palmLocal).applyQuaternion(_handWQ).normalize();

        const twistAxisW = _desFingerW;

        const curP = _tmpA.copy(_curPalmW).projectOnPlane(twistAxisW);
        const desP = _tmpB.copy(_desPalmW).projectOnPlane(twistAxisW);

        if (curP.lengthSq() > 1e-10 && desP.lengthSq() > 1e-10) {
            curP.normalize();
            desP.normalize();
            const cross = _tmpC.crossVectors(curP, desP);
            const sign = Math.sign(cross.dot(twistAxisW)) || 1;
            const dot = THREE.MathUtils.clamp(curP.dot(desP), -1, 1);
            const fullTwist = sign * Math.acos(dot);
            applyWorldAxisRotationToBone(handBone, twistAxisW, fullTwist * alpha);
        }
    }

    return {
        defaultFingerDirLocal,
        defaultPalmNormalLocal,
        applyHandOrientationConstraint,
    };
}

// ====================
// Fingers (curl direction fixed)
// ====================
export function makeFingerRig(bonesByName) {
    const fingerNames = [
        ["thumb_01", "thumb_02", "thumb_03"],
        ["index_01", "index_02", "index_03"],
        ["middle_01", "middle_02", "middle_03"],
        ["ring_01", "ring_02", "ring_03"],
        ["pinky_01", "pinky_02", "pinky_03"],
    ];

    const groups = [];
    for (const trio of fingerNames) {
        const arr = [];
        for (const base of trio) {
            const b = bonesByName.get(base) || null;
            if (b) arr.push({ bone: b, rest: b.quaternion.clone() });
        }
        groups.push(arr);
    }

    const curlAxisLocal = new THREE.Vector3(1, 0, 0);

    function applyCurl(amount01) {
        const a = 0.8 * THREE.MathUtils.clamp(amount01, 0, 1);

        const baseAng = 1.1 * a;
        const midAng = 1.0 * a;
        const tipAng = 0.8 * a;

        for (const finger of groups) {
            for (let i = 0; i < finger.length; i++) {
                const { bone, rest } = finger[i];
                bone.quaternion.copy(rest);
                const ang = (i === 0) ? baseAng : (i === 1) ? midAng : tipAng;
                const q = new THREE.Quaternion().setFromAxisAngle(curlAxisLocal, ang);
                bone.quaternion.multiply(q);
            }
        }
    }
    return { applyCurl };
}

// ====================
// Cylinder helpers (world bbox + axis + radius)
// ====================
const _cylBox = new THREE.Box3();
const _cylSize = new THREE.Vector3();
const _cylCenter = new THREE.Vector3();
const _cylWorldQ = new THREE.Quaternion();
const _cylWorldS = new THREE.Vector3();

export function getCylinderWorldInfo(cylMesh) {
    cylMesh.updateWorldMatrix(true, true);

    _cylBox.setFromObject(cylMesh);
    _cylBox.getSize(_cylSize);
    _cylBox.getCenter(_cylCenter);

    cylMesh.getWorldQuaternion(_cylWorldQ);
    const axisW = new THREE.Vector3(0, 1, 0).applyQuaternion(_cylWorldQ).normalize();

    let radiusW = Math.max(_cylSize.x, _cylSize.z) * 0.5;
    const g = cylMesh.geometry;
    if (g && g.parameters && (g.parameters.radiusTop != null || g.parameters.radiusBottom != null)) {
        const r = Math.max(g.parameters.radiusTop ?? 0, g.parameters.radiusBottom ?? 0);
        cylMesh.getWorldScale(_cylWorldS);
        radiusW = r * Math.max(_cylWorldS.x, _cylWorldS.z);
    }

    const topW = new THREE.Vector3(_cylCenter.x, _cylBox.max.y, _cylCenter.z);
    const belowTopOffset = -0.05;
    const graspCenterW = topW.clone().add(axisW.clone().multiplyScalar(belowTopOffset));

    return {
        bbox: _cylBox.clone(),
        centerW: _cylCenter.clone(),
        axisW,
        radiusW,
        topW,
        graspCenterW
    };
}

// ====================
// Grabbables
// ====================
// A GrabbableObject provides a grasp pose (position + desired hand orientation)
// so an Arm can move to it.
export class GrabbableObject {
    constructor({
        name = "grabbable",
        object3d = null,
        getGraspPose = null,
    } = {}) {
        this.name = name;
        this.object3d = object3d;

        if (typeof getGraspPose !== "function") {
            throw new Error("GrabbableObject: getGraspPose must be a function");
        }
        this._getGraspPose = getGraspPose;
    }

    // Returns:
    // {
    //   targetWorld: THREE.Vector3,
    //   desiredFingerDirWorld: THREE.Vector3,
    //   desiredPalmNormalWorld: THREE.Vector3,
    // }
    getGraspPose({ person, arm } = {}) {
        return this._getGraspPose({ person, arm, object3d: this.object3d, grabbable: this });
    }
}

// Convenience factory mirroring the old moveHandToCylinder behavior.
export function makeCylinderGrabbable(
    cylMesh,
    {
        name = null,
        clearance = 0.02,
        belowTopOffset = -0.05,
    } = {}
) {
    const tmpForwardW = new THREE.Vector3();
    const tmpUpW = new THREE.Vector3(0, 1, 0);
    const tmpRightW = new THREE.Vector3();
    const tmpOffsetDirW = new THREE.Vector3();
    const tmpPalmNormalW = new THREE.Vector3();
    const tmpFingerDirW = new THREE.Vector3();
    const tmpTargetW = new THREE.Vector3();

    return new GrabbableObject({
        name: name ?? (cylMesh?.name || "cylinder"),
        object3d: cylMesh,
        getGraspPose: ({ person, arm, object3d }) => {
            if (!person) throw new Error("makeCylinderGrabbable.getGraspPose: person is required");
            if (!arm) throw new Error("makeCylinderGrabbable.getGraspPose: arm is required");
            if (!object3d) throw new Error("makeCylinderGrabbable.getGraspPose: cylMesh is required");

            const info = getCylinderWorldInfo(object3d);

            // Old behavior: finger points forward (person facing dir), palm faces in toward cylinder.
            person.getFacingDirWorldXZ(tmpForwardW);
            tmpRightW.crossVectors(tmpForwardW, tmpUpW).normalize();

            const sideSign = (arm.name === "left") ? -1 : 1;
            tmpOffsetDirW.copy(tmpRightW).multiplyScalar(sideSign);
            tmpPalmNormalW.copy(tmpOffsetDirW).multiplyScalar(-1).normalize();
            tmpFingerDirW.copy(tmpForwardW).normalize();

            // Slightly below cylinder top, offset laterally by radius+clearance.
            tmpTargetW.copy(info.topW);
            tmpTargetW.addScaledVector(info.axisW, belowTopOffset);
            tmpTargetW.addScaledVector(tmpOffsetDirW, info.radiusW + clearance);

            return {
                targetWorld: tmpTargetW.clone(),
                desiredFingerDirWorld: tmpFingerDirW.clone(),
                desiredPalmNormalWorld: tmpPalmNormalW.clone(),
            };
        },
    });
}

// ====================
// Arm + ArmsPerson
// ====================
export class Arm {
    constructor({
        name,
        chainBones,
        endEffectorBone,
        handBone,
        forearmBone,
        bonesByNameForFingers,
        solveFn,
        logFn,
        scene,
        targetColor,
        effectorColor,
        ownerPerson,
        applyHandOrientationConstraint,
    }) {
        this.name = name;
        this.chain = chainBones;
        this.endEffector = endEffectorBone;
        this.handBone = handBone;
        this.forearmBone = forearmBone;
        this.owner = ownerPerson;

        this.solveCCD = solveFn;
        this.log = logFn;
        this.applyHandOrientationConstraint = applyHandOrientationConstraint || null;

        this.reachedEps = 0.012;
        this.maxItersPerStep = 22;
        this.maxStep = Math.PI / 18;

        this.targetWorld = new THREE.Vector3();
        this._dirty = true;

        this._tmpEff = new THREE.Vector3();

        // Optional: virtual end-effector point (child of handBone) computed from a
        // weighted mixture of three joint positions + plane-normal offset.
        this._endEffectorPlane = null;
        this._endEffectorObj = null;
        this._tmpA_W = new THREE.Vector3();
        this._tmpB_W = new THREE.Vector3();
        this._tmpC_W = new THREE.Vector3();
        this._tmpA_L = new THREE.Vector3();
        this._tmpB_L = new THREE.Vector3();
        this._tmpC_L = new THREE.Vector3();
        this._tmpU_L = new THREE.Vector3();
        this._tmpV_L = new THREE.Vector3();
        this._tmpN_L = new THREE.Vector3();

        const effector_size = 0.01;

        this.targetMarker = new THREE.Mesh(
            new THREE.SphereGeometry(effector_size, 16, 16),
            new THREE.MeshBasicMaterial({ color: targetColor, transparent: true, opacity: 0.5 })
        );
        this.effectorMarker = new THREE.Mesh(
            new THREE.SphereGeometry(effector_size, 16, 16),
            new THREE.MeshBasicMaterial({ color: effectorColor, transparent: true, opacity: 0.5 })
        );
        scene.add(this.targetMarker);
        scene.add(this.effectorMarker);

        this._hasOrientTarget = false;
        this._desiredFingerDirW = new THREE.Vector3(0, 0, -1);
        this._desiredPalmNormalW = new THREE.Vector3(-1, 0, 0);

        this._fingerCurl = 0.0;
        this._fingerCurlTarget = 0.0;
        this._fingerRig = makeFingerRig(bonesByNameForFingers);

        this._overrideTargetWorld = null;
        this._everSet = false;
    }

    // Configure a virtual end-effector point defined in the hand's local space by:
    // - three joint positions (A,B,C) which define a plane
    // - a non-negative weight vector [wA,wB,wC] to pick a point inside the triangle
    //   (e.g. [1,1,1] = centroid; [2,1,1] biases toward A)
    // - an offset scalar along the plane normal (in hand-local units)
    // The resulting point is stored on an Object3D parented to the handBone so it
    // moves with the hand and works with CCD.
    usePlaneMixtureEndEffector({
        jointA,
        jointB,
        jointC,
        weights = [1, 1, 1],
        normalOffset = 0.0,
        normalSign = 1.0,
        name = null,
    } = {}) {
        if (!this.handBone) throw new Error("Arm.usePlaneMixtureEndEffector: handBone is required");
        if (!jointA || !jointB || !jointC) throw new Error("Arm.usePlaneMixtureEndEffector: jointA/jointB/jointC are required");

        if (!this._endEffectorObj) {
            this._endEffectorObj = new THREE.Object3D();
            this._endEffectorObj.name = name ?? `${this.name}_plane_effector`;
            this.handBone.add(this._endEffectorObj);
        }

        this._endEffectorPlane = {
            jointA,
            jointB,
            jointC,
            weights: Array.isArray(weights) ? weights.slice(0, 3) : [1, 1, 1],
            normalOffset: Number.isFinite(normalOffset) ? normalOffset : 0.0,
            normalSign: Number.isFinite(normalSign) ? normalSign : 1.0,
        };

        // Use the virtual object as the end effector for CCD and marker visualization.
        this.endEffector = this._endEffectorObj;
        this._updatePlaneMixtureEffector();
        this.log(
            `Arm(${this.name}): using plane-mixture end effector ` +
            `(w=${this._endEffectorPlane.weights.map(x => Number(x).toFixed(2)).join(",")}, ` +
            `offset=${this._endEffectorPlane.normalOffset.toFixed(3)})`
        );
    }

    setPlaneMixtureWeights(weights) {
        if (!this._endEffectorPlane) return;
        if (!Array.isArray(weights) || weights.length < 3) return;
        this._endEffectorPlane.weights = weights.slice(0, 3);
        this._updatePlaneMixtureEffector();
    }

    setPlaneMixtureNormalOffset(normalOffset) {
        if (!this._endEffectorPlane) return;
        if (!Number.isFinite(normalOffset)) return;
        this._endEffectorPlane.normalOffset = normalOffset;
        this._updatePlaneMixtureEffector();
    }

    _updatePlaneMixtureEffector() {
        if (!this._endEffectorPlane || !this._endEffectorObj || !this.handBone) return;
        const { jointA, jointB, jointC, weights, normalOffset, normalSign } = this._endEffectorPlane;
        if (!jointA || !jointB || !jointC) return;

        // Read world positions.
        jointA.updateWorldMatrix(true, false);
        jointB.updateWorldMatrix(true, false);
        jointC.updateWorldMatrix(true, false);
        jointA.getWorldPosition(this._tmpA_W);
        jointB.getWorldPosition(this._tmpB_W);
        jointC.getWorldPosition(this._tmpC_W);

        // Convert to hand local space so the effector is stable as a child of handBone.
        this.handBone.updateWorldMatrix(true, false);
        this._tmpA_L.copy(this._tmpA_W); this.handBone.worldToLocal(this._tmpA_L);
        this._tmpB_L.copy(this._tmpB_W); this.handBone.worldToLocal(this._tmpB_L);
        this._tmpC_L.copy(this._tmpC_W); this.handBone.worldToLocal(this._tmpC_L);

        const wA = Number.isFinite(weights?.[0]) ? weights[0] : 1;
        const wB = Number.isFinite(weights?.[1]) ? weights[1] : 1;
        const wC = Number.isFinite(weights?.[2]) ? weights[2] : 1;
        const wSum = wA + wB + wC;
        const inv = Math.abs(wSum) > 1e-12 ? (1.0 / wSum) : (1.0 / 3.0);

        // Weighted mixture point in-plane.
        this._endEffectorObj.position
            .set(0, 0, 0)
            .addScaledVector(this._tmpA_L, wA * inv)
            .addScaledVector(this._tmpB_L, wB * inv)
            .addScaledVector(this._tmpC_L, wC * inv);

        // Plane normal in hand-local space (orientation from joint order).
        this._tmpU_L.copy(this._tmpB_L).sub(this._tmpA_L);
        this._tmpV_L.copy(this._tmpC_L).sub(this._tmpA_L);
        this._tmpN_L.crossVectors(this._tmpU_L, this._tmpV_L);
        if (this._tmpN_L.lengthSq() > 1e-12) {
            this._tmpN_L.normalize();
            this._tmpN_L.multiplyScalar(Number.isFinite(normalSign) ? normalSign : 1.0);
            this._endEffectorObj.position.addScaledVector(this._tmpN_L, Number.isFinite(normalOffset) ? normalOffset : 0.0);
        }

        this._endEffectorObj.updateMatrixWorld(true);
    }

    setEffectorTarget(worldPos) {
        const changed = this.targetWorld.distanceToSquared(worldPos) > 1e-10;
        if (changed || !this._everSet) {
            this.targetWorld.copy(worldPos);
            this.targetMarker.position.copy(this.targetWorld);
            this._dirty = true;
            this._everSet = true;
        }
    }

    setOverrideTargetWorld(worldPosOrNull) {
        this._overrideTargetWorld = worldPosOrNull ? worldPosOrNull.clone() : null;
        if (this._overrideTargetWorld) {
            this.setEffectorTarget(this._overrideTargetWorld);
            this.log(`Arm(${this.name}): override target set -> ${fmtV(this._overrideTargetWorld)}`);
        } else {
            this.log(`Arm(${this.name}): override target cleared`);
            this._hasOrientTarget = false;
        }
    }

    step(dt) {
        if (!this.endEffector || !this.chain) return;

        // Keep a virtual end-effector point in sync with the current hand pose.
        if (this._endEffectorPlane) this._updatePlaneMixtureEffector();

        this.endEffector.getWorldPosition(this._tmpEff);
        this.effectorMarker.position.copy(this._tmpEff);

        this._fingerCurl += (this._fingerCurlTarget - this._fingerCurl) * (1 - Math.exp(-dt * 10));
        this._fingerRig.applyCurl(this._fingerCurl);

        if (!this._dirty) {
            if (this._hasOrientTarget && this.applyHandOrientationConstraint) {
                this.applyHandOrientationConstraint({
                    handBone: this.handBone,
                    forearmBone: this.forearmBone,
                    desiredFingerDirWorld: this._desiredFingerDirW,
                    desiredPalmNormalWorld: this._desiredPalmNormalW,
                    dt
                });
            }
            return;
        }

        const dist0 = this._tmpEff.distanceTo(this.targetWorld);
        if (dist0 <= this.reachedEps) {
            this._dirty = false;
            return;
        }

        this.solveCCD(this.chain, this.endEffector, this.targetWorld, {
            iters: this.maxItersPerStep,
            threshold: this.reachedEps,
            maxStep: this.maxStep
        });

        if (this._hasOrientTarget && this.applyHandOrientationConstraint) {
            this.applyHandOrientationConstraint({
                handBone: this.handBone,
                forearmBone: this.forearmBone,
                desiredFingerDirWorld: this._desiredFingerDirW,
                desiredPalmNormalWorld: this._desiredPalmNormalW,
                dt
            });
        }

        this.endEffector.getWorldPosition(this._tmpEff);
        if (this._tmpEff.distanceTo(this.targetWorld) <= this.reachedEps) {
            this._dirty = false;
        }
    }

    // Goal: fingers point FORWARD (person forward), palm faces LEFT (person left).
    // We place the hand slightly to the RIGHT of the cylinder by radius+clearance so the palm faces it.
    moveHandToCylinder(cylMesh) {
        if (!this.owner || !cylMesh) return;

        const info = getCylinderWorldInfo(cylMesh);

        const forwardW = this.owner.getFacingDirWorldXZ(new THREE.Vector3());
        const upW = new THREE.Vector3(0, 1, 0);
        const rightW = new THREE.Vector3().crossVectors(forwardW, upW).normalize();
        const leftW = rightW.clone().multiplyScalar(-1);

        this._desiredFingerDirW.copy(forwardW);
        this._desiredPalmNormalW.copy(leftW);
        this._hasOrientTarget = true;

        const clearance = 0.02;
        const handCenterW = info.graspCenterW
            .clone()
            .add(rightW.clone().multiplyScalar(info.radiusW + clearance));

        this.setOverrideTargetWorld(handCenterW);

        this.log(
            `Arm.moveHandToCylinder(${this.name}):` +
            ` cylRadius=${info.radiusW.toFixed(3)} grasp=${fmtV(info.graspCenterW)} target=${fmtV(handCenterW)}`
        );
    }

    moveHandToGrabbable(grabbable) {
        if (!this.owner || !grabbable) return;

        const getPose = (g) => {
            if (g instanceof GrabbableObject) return g.getGraspPose({ person: this.owner, arm: this });
            if (typeof g.getGraspPose === "function") return g.getGraspPose({ person: this.owner, arm: this });
            return null;
        };

        let pose = null;
        try {
            pose = getPose(grabbable);
        } catch (e) {
            this.log(`Arm.moveHandToGrabbable(${this.name}): ERROR computing grasp pose: ${e?.message || e}`);
            return;
        }

        const targetWorld = pose?.targetWorld;
        const desiredFingerDirWorld = pose?.desiredFingerDirWorld;
        const desiredPalmNormalWorld = pose?.desiredPalmNormalWorld;

        if (!targetWorld || !desiredFingerDirWorld || !desiredPalmNormalWorld) {
            this.log(`Arm.moveHandToGrabbable(${this.name}): invalid grasp pose for ${grabbable?.name || "(unnamed)"}`);
            return;
        }

        this._desiredFingerDirW.copy(desiredFingerDirWorld);
        this._desiredPalmNormalW.copy(desiredPalmNormalWorld);
        this._hasOrientTarget = true;

        this.setOverrideTargetWorld(targetWorld);
        this.log(
            `Arm.moveHandToGrabbable(${this.name}): ${grabbable?.name || "grabbable"}` +
            ` target=${fmtV(targetWorld)} finger=${fmtV(this._desiredFingerDirW)} palm=${fmtV(this._desiredPalmNormalW)}`
        );
    }

    closeHandAroundCylinder() {
        this._fingerCurlTarget = 1.0;
        this.log(`Arm.closeHandAroundCylinder(${this.name})`);
    }

    openHand() {
        this._fingerCurlTarget = 0.0;
    }
}

export class ArmsPerson {
    constructor({ scene, logFn }) {
        this.log = logFn;

        this.root = new THREE.Group();
        scene.add(this.root);

        this.root.position.set(0.0, 2.0, -0.2);

        this.rigWrap = new THREE.Group();
        this.root.add(this.rigWrap);

        this.rigWrap.rotation.set(
            THREE.MathUtils.degToRad(0),
            THREE.MathUtils.degToRad(180),
            THREE.MathUtils.degToRad(0)
        );

        this.yaw = 0;
        this.turnSpeed = THREE.MathUtils.degToRad(90);
        this.walkSpeed = 0.9;

        this.centerLocal = new THREE.Vector3(0, 0, 0);
        this.forwardLocal = new THREE.Vector3(0, 0, -1);

        // These offsets are tuned for the historical default desiredHeight=0.9.
        // If you change desiredHeight, you must scale these offsets too, otherwise
        // the IK targets stay “too far away” and the arms will stretch.
        this._baseDesiredHeight = 0.9;
        this._baseLeftOffsetLocal = new THREE.Vector3(-0.45, -1.15, 0.05);
        this._baseRightOffsetLocal = new THREE.Vector3(0.45, -1.15, 0.05);
        this.leftOffsetLocal = this._baseLeftOffsetLocal.clone();
        this.rightOffsetLocal = this._baseRightOffsetLocal.clone();

        this.desiredHeight = this._baseDesiredHeight;
        this.desiredHeightScale = 1.0;

        this.leftArm = null;
        this.rightArm = null;

        this._leftTargetW = new THREE.Vector3();
        this._rightTargetW = new THREE.Vector3();
        this._tmpForward = new THREE.Vector3();

        this._wl = new THREE.Vector3();
        this._wr = new THREE.Vector3();
        this._midW = new THREE.Vector3();
        this._midLocal = new THREE.Vector3();
    }

    setDesiredHeight(desiredHeight, { baseDesiredHeight = this._baseDesiredHeight } = {}) {
        if (!Number.isFinite(desiredHeight) || desiredHeight <= 0) return;
        const s = desiredHeight / Math.max(1e-9, baseDesiredHeight);
        this.desiredHeight = desiredHeight;
        this.desiredHeightScale = s;

        this.leftOffsetLocal.copy(this._baseLeftOffsetLocal).multiplyScalar(s);
        this.rightOffsetLocal.copy(this._baseRightOffsetLocal).multiplyScalar(s);
    }

    addRigScene(gltfScene) {
        this.rigRoot = gltfScene;
        this.rigWrap.add(this.rigRoot);
    }

    recenterRigToShoulders(leftShoulderBone, rightShoulderBone) {
        leftShoulderBone.getWorldPosition(this._wl);
        rightShoulderBone.getWorldPosition(this._wr);

        this._midW.copy(this._wl).add(this._wr).multiplyScalar(0.5);
        this._midLocal.copy(this._midW);
        this.root.worldToLocal(this._midLocal);

        this.rigWrap.position.sub(this._midLocal);
        this.rigWrap.updateWorldMatrix(true, true);

        this.log(`Recenter: rigWrap.pos=${fmtV(this.rigWrap.position)} (sub midLocal=${fmtV(this._midLocal)})`);
    }

    getFacingDirWorldXZ(out) {
        out.copy(this.forwardLocal);
        out.applyQuaternion(this.root.quaternion);
        out.y = 0;
        out.normalize();
        return out;
    }

    offsetLocalToWorld(offsetLocal, out) {
        out.copy(this.centerLocal).add(offsetLocal);
        return this.root.localToWorld(out);
    }

    nudgeRightOffset(deltaLR, deltaFB, deltaY) {
        if (this.rightArm && this.rightArm._overrideTargetWorld) {
            this.log("Right arm override active; arrow nudges ignored");
            return;
        }
        this.rightOffsetLocal.x += deltaLR;
        this.rightOffsetLocal.z -= deltaFB;
        this.rightOffsetLocal.y += deltaY;
    }

    update(dt, keys) {
        let turn = 0;
        if (keys.ctrl) turn += 1;
        if (keys.space) turn -= 1;
        if (turn !== 0) {
            this.yaw += turn * this.turnSpeed * dt;
            this.root.rotation.y = this.yaw;
        }

        if (keys.a) {
            this.getFacingDirWorldXZ(this._tmpForward);
            this._tmpForward.multiplyScalar(this.walkSpeed * dt);
            this.root.position.add(this._tmpForward);
        }

        if (this.leftArm && this.rightArm) {
            this.offsetLocalToWorld(this.leftOffsetLocal, this._leftTargetW);
            this.leftArm.setEffectorTarget(this._leftTargetW);

            if (this.rightArm._overrideTargetWorld) {
                this.rightArm.setEffectorTarget(this.rightArm._overrideTargetWorld);
            } else {
                this.offsetLocalToWorld(this.rightOffsetLocal, this._rightTargetW);
                this.rightArm.setEffectorTarget(this._rightTargetW);
            }

            this.leftArm.step(dt);
            this.rightArm.step(dt);
        }
    }
}

// ====================
// Skeleton mode controller (bones + joints + tooltips)
// ====================
export function createSkeletonModeController({
    scene,
    camera,
    renderer,
    tooltipEl,
    logFn,
    jointRadius = 0.01,
    defaultFingerDirLocal,
    defaultPalmNormalLocal,
} = {}) {
    let skeletonMode = false;

    let cameraRef = camera || null;

    let rigRootRef = null;
    let skeletonBones = [];
    let rightHandBoneRef = null;
    let leftClavRef = null;
    let rightClavRef = null;

    let jointPointsGroup = null;
    let jointSpheres = [];
    let boneLinesGroup = null;
    let boneLines = [];

    let defaultVecGroup = null;
    let defaultFingerArrow = null;
    let defaultPalmArrow = null;
    let defaultThirdHandArrow = null;

    let raycastTargets = [];
    const raycaster = new THREE.Raycaster();
    raycaster.params.Line.threshold = 0.03;
    const mouseNDC = new THREE.Vector2();
    let lastMouseClient = { x: 0, y: 0 };

    const _p = new THREE.Vector3();
    const _p0 = new THREE.Vector3();
    const _p1 = new THREE.Vector3();

    function setTooltipVisible(show, text, clientX, clientY) {
        if (!tooltipEl) return;
        if (!show) {
            tooltipEl.style.display = "none";
            return;
        }
        tooltipEl.style.display = "block";
        tooltipEl.textContent = text;
        tooltipEl.style.left = `${clientX}px`;
        tooltipEl.style.top = `${clientY}px`;
    }

    function setMeshOpacity(root, opacity) {
        root.traverse(o => {
            if (o.isSkinnedMesh) {
                const mats = Array.isArray(o.material) ? o.material : [o.material];
                for (const m of mats) {
                    if (!m) continue;
                    m.transparent = opacity < 1.0;
                    m.opacity = opacity;
                    m.depthWrite = opacity >= 1.0;
                    m.needsUpdate = true;
                }
            }
        });
    }

    function buildJointPoints(bones) {
        const g = new THREE.Group();
        g.name = "JointPoints";
        const geom = new THREE.SphereGeometry(jointRadius, 10, 10);
        const mat = new THREE.MeshBasicMaterial({ color: 0xff9900 });

        const arr = [];
        for (const b of bones) {
            const s = new THREE.Mesh(geom, mat);
            const parentName = b?.parent?.name || "(none)";
            s.userData.hoverText = `JOINT: ${b.name}\nparent: ${parentName}`;
            g.add(s);
            arr.push({ bone: b, mesh: s });
        }
        return { group: g, joints: arr };
    }

    function buildBoneLines(bones) {
        const g = new THREE.Group();
        g.name = "BoneLines";
        const mat = new THREE.LineBasicMaterial({ color: 0x7fd3ff });

        const lines = [];
        for (const b of bones) {
            if (!b.parent || !b.parent.isBone) continue;
            if (b.name === "_rootJoint" || b.parent.name === "_rootJoint") continue;

            const positions = new Float32Array(6);
            const geo = new THREE.BufferGeometry();
            geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));

            const line = new THREE.Line(geo, mat);
            line.frustumCulled = false;
            line.userData.hoverText = `BONE: ${b.name}\nparent: ${b.parent.name}`;
            g.add(line);

            lines.push({ bone: b, parentBone: b.parent, line, positions });
        }
        return { group: g, lines };
    }

    function ensureDefaultVecGizmos() {
        if (!rightHandBoneRef) return;
        if (!defaultFingerDirLocal || !defaultPalmNormalLocal) return;

        if (!defaultVecGroup) {
            defaultVecGroup = new THREE.Group();
            scene.add(defaultVecGroup);

            defaultFingerArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 0.35, 0x00ff66);
            defaultPalmArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 0.35, 0xff00ff);
            defaultThirdHandArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(), 0.35, 0x0000ff);

            defaultVecGroup.add(defaultFingerArrow);
            defaultVecGroup.add(defaultPalmArrow);
            defaultVecGroup.add(defaultThirdHandArrow);

            const tipGeom = new THREE.SphereGeometry(0.02, 10, 10);
            const tipMat = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.0 });

            const tip1 = new THREE.Mesh(tipGeom, tipMat);
            tip1.userData.hoverText = `DEFAULT_FINGER_DIR_LOCAL = ${fmtV(defaultFingerDirLocal)} (hand local)\n(green arrow)`;

            const tip2 = new THREE.Mesh(tipGeom, tipMat);
            tip2.userData.hoverText = `DEFAULT_PALM_NORMAL_LOCAL = ${fmtV(defaultPalmNormalLocal)} (hand local)\n(magenta arrow)`;

            defaultVecGroup.add(tip1);
            defaultVecGroup.add(tip2);
            defaultVecGroup.userData._fingerTip = tip1;
            defaultVecGroup.userData._palmTip = tip2;
        }
    }

    function updateSkeletonGizmos() {
        if (!skeletonMode) return;

        if (jointSpheres.length) {
            for (const js of jointSpheres) {
                if (js.bone.name === "_rootJoint" && leftClavRef && rightClavRef) {
                    leftClavRef.getWorldPosition(_p0);
                    rightClavRef.getWorldPosition(_p1);
                    _p.copy(_p0).add(_p1).multiplyScalar(0.5);
                    js.mesh.position.copy(_p);
                    js.mesh.userData.hoverText =
                        `JOINT: _rootJoint\n` +
                        `(visualized at clavicle midpoint for debugging)\n` +
                        `world: ${fmtV(_p)}\n` +
                        `actual bone position may be elsewhere in file`;
                } else {
                    js.bone.getWorldPosition(_p);
                    js.mesh.position.copy(_p);
                    const parentName = js?.bone?.parent?.name || "(none)";
                    js.mesh.userData.hoverText =
                        `JOINT: ${js.bone.name}\n` +
                        `parent: ${parentName}\n` +
                        `world: ${fmtV(_p)}`;
                }
            }
        }

        if (boneLines.length) {
            for (const bl of boneLines) {
                bl.parentBone.getWorldPosition(_p0);
                bl.bone.getWorldPosition(_p1);
                bl.positions[0] = _p0.x; bl.positions[1] = _p0.y; bl.positions[2] = _p0.z;
                bl.positions[3] = _p1.x; bl.positions[4] = _p1.y; bl.positions[5] = _p1.z;
                bl.line.geometry.attributes.position.needsUpdate = true;
                bl.line.geometry.computeBoundingSphere();
            }
        }

        if (defaultVecGroup && rightHandBoneRef && defaultFingerArrow && defaultPalmArrow && defaultThirdHandArrow) {
            const handPos = new THREE.Vector3();
            const handQ = new THREE.Quaternion();
            rightHandBoneRef.getWorldPosition(handPos);
            rightHandBoneRef.getWorldQuaternion(handQ);

            const fingerW = defaultFingerDirLocal.clone().normalize().applyQuaternion(handQ).normalize();
            const palmW = defaultPalmNormalLocal.clone().normalize().applyQuaternion(handQ).normalize();

            defaultFingerArrow.position.copy(handPos);
            defaultFingerArrow.setDirection(fingerW);

            defaultPalmArrow.position.copy(handPos);
            defaultPalmArrow.setDirection(palmW);

            defaultThirdHandArrow.position.copy(handPos);
            const thirdW = new THREE.Vector3().crossVectors(fingerW, palmW);
            if (thirdW.lengthSq() < 1e-12) thirdW.set(0, 1, 0).applyQuaternion(handQ);
            defaultThirdHandArrow.setDirection(thirdW.normalize());

            const tip1 = defaultVecGroup.userData._fingerTip;
            const tip2 = defaultVecGroup.userData._palmTip;
            if (tip1 && tip2) {
                tip1.position.copy(handPos).add(fingerW.clone().multiplyScalar(0.35));
                tip2.position.copy(handPos).add(palmW.clone().multiplyScalar(0.35));
            }
        }
    }

    function performHoverRaycast() {
        if (!skeletonMode || raycastTargets.length === 0) {
            setTooltipVisible(false);
            return;
        }

        if (!cameraRef) {
            setTooltipVisible(false);
            return;
        }

        const rect = renderer.domElement.getBoundingClientRect();
        mouseNDC.x = ((lastMouseClient.x - rect.left) / rect.width) * 2 - 1;
        mouseNDC.y = -(((lastMouseClient.y - rect.top) / rect.height) * 2 - 1);

        raycaster.setFromCamera(mouseNDC, cameraRef);
        const hits = raycaster.intersectObjects(raycastTargets, true);

        if (hits.length === 0) {
            setTooltipVisible(false);
            return;
        }

        for (const h of hits) {
            const o = h.object;
            if (o?.userData?.hoverText) {
                setTooltipVisible(true, o.userData.hoverText, lastMouseClient.x, lastMouseClient.y);
                return;
            }
        }

        setTooltipVisible(false);
    }

    function rebuildRaycastTargets() {
        raycastTargets = [];
        for (const js of jointSpheres) raycastTargets.push(js.mesh);
        for (const bl of boneLines) raycastTargets.push(bl.line);
        if (defaultVecGroup?.userData?._fingerTip) raycastTargets.push(defaultVecGroup.userData._fingerTip);
        if (defaultVecGroup?.userData?._palmTip) raycastTargets.push(defaultVecGroup.userData._palmTip);
    }

    function toggle() {
        if (!rigRootRef) return;

        skeletonMode = !skeletonMode;
        if (logFn) logFn(`SKELETON MODE: ${skeletonMode ? "ON" : "OFF"}`);

        if (skeletonMode) {
            setMeshOpacity(rigRootRef, 0.10);

            if (!jointPointsGroup) {
                const { group, joints } = buildJointPoints(skeletonBones);
                jointPointsGroup = group;
                jointSpheres = joints;
                scene.add(jointPointsGroup);
            }

            if (!boneLinesGroup) {
                const { group, lines } = buildBoneLines(skeletonBones);
                boneLinesGroup = group;
                boneLines = lines;
                scene.add(boneLinesGroup);
            }

            ensureDefaultVecGizmos();
            rebuildRaycastTargets();
        } else {
            setMeshOpacity(rigRootRef, 1.0);

            if (jointPointsGroup) {
                scene.remove(jointPointsGroup);
                jointPointsGroup = null;
                jointSpheres = [];
            }
            if (boneLinesGroup) {
                scene.remove(boneLinesGroup);
                boneLinesGroup = null;
                boneLines = [];
            }
            if (defaultVecGroup) {
                scene.remove(defaultVecGroup);
                defaultVecGroup = null;
                defaultFingerArrow = null;
                defaultPalmArrow = null;
            }
            raycastTargets = [];
            setTooltipVisible(false);
        }
    }

    function onMouseMove(e) {
        lastMouseClient.x = e.clientX;
        lastMouseClient.y = e.clientY;
    }

    function update() {
        updateSkeletonGizmos();
        performHoverRaycast();
    }

    function setRig({ rigRoot, bones, rightHandBone, leftClav, rightClav } = {}) {
        rigRootRef = rigRoot || null;
        skeletonBones = bones || [];
        rightHandBoneRef = rightHandBone || null;
        leftClavRef = leftClav || null;
        rightClavRef = rightClav || null;
    }

    function setCamera(nextCamera) {
        cameraRef = nextCamera || null;
    }

    return {
        toggle,
        update,
        onMouseMove,
        setCamera,
        setRig,
        get enabled() { return skeletonMode; },
    };
}

// ====================
// Rig helpers
// ====================
export function findByName(root, name) {
    let found = null;
    root.traverse(o => { if (o.name === name) found = o; });
    return found;
}

export function findSkinnedMesh(root) {
    let s = null;
    root.traverse(o => { if (o.isSkinnedMesh && !s) s = o; });
    return s;
}

export function setSkinnedMaterialNice(root) {
    root.traverse(o => {
        if (o.isSkinnedMesh) {
            const mat = new THREE.MeshStandardMaterial({ color: 0xdddddd, roughness: 0.75 });
            mat.skinning = true;
            o.material = mat;
            o.material.needsUpdate = true;
        }
    });
}

export function fitToHeight(obj, desiredHeight = 0.9) {
    obj.updateWorldMatrix(true, true);
    const box0 = new THREE.Box3().setFromObject(obj);
    const size0 = new THREE.Vector3();
    box0.getSize(size0);

    const scale = desiredHeight / Math.max(1e-9, size0.y);
    obj.scale.setScalar(scale);

    obj.updateWorldMatrix(true, true);
    const box1 = new THREE.Box3().setFromObject(obj);
    const center1 = new THREE.Vector3();
    box1.getCenter(center1);

    obj.position.x += -center1.x;
    obj.position.z += -center1.z;
    obj.position.y += -box1.min.y;

    obj.updateWorldMatrix(true, true);
    const box2 = new THREE.Box3().setFromObject(obj);
    return { scale, box: box2 };
}

export function frameCameraToBox(box, { camera, controls }) {
    const size = new THREE.Vector3();
    box.getSize(size);
    const center = new THREE.Vector3();
    box.getCenter(center);
    const radius = Math.max(size.x, size.y, size.z) * 0.5;
    const dist = Math.max(0.9, radius * 2.8);

    controls.target.copy(center);
    camera.position.copy(center).add(new THREE.Vector3(dist * 0.25, dist * 0.55, dist));
    controls.update();
}

export function cacheBones(skinnedMesh) {
    const bones = new Map();
    for (const b of skinnedMesh.skeleton.bones) bones.set(b.name, b);
    return bones;
}

export function buildFingerMap(side, bonesMap) {
    const m = new Map();
    const suffix = (side === "r") ? "_r" : "_l";
    function pick(prefix) {
        for (const k of bonesMap.keys()) {
            if (k.startsWith(prefix + suffix)) return bonesMap.get(k);
        }
        return null;
    }
    m.set("thumb_01", pick("thumb_01")); m.set("thumb_02", pick("thumb_02")); m.set("thumb_03", pick("thumb_03"));
    m.set("index_01", pick("index_01")); m.set("index_02", pick("index_02")); m.set("index_03", pick("index_03"));
    m.set("middle_01", pick("middle_01")); m.set("middle_02", pick("middle_02")); m.set("middle_03", pick("middle_03"));
    m.set("ring_01", pick("ring_01")); m.set("ring_02", pick("ring_02")); m.set("ring_03", pick("ring_03"));
    m.set("pinky_01", pick("pinky_01")); m.set("pinky_02", pick("pinky_02")); m.set("pinky_03", pick("pinky_03"));
    return m;
}

export function getLeftArmBones(bonesMap) {
    return {
        shoulder: bonesMap.get("clavicle_l_01"),
        upperarm: bonesMap.get("upperarm_l_02"),
        forearm: bonesMap.get("lowerarm_l_03"),
        hand: bonesMap.get("hand_l_04"),
        middle_eff: bonesMap.get("middle_01_l_07"),
    };
}

export function getRightArmBones(bonesMap) {
    return {
        shoulder: bonesMap.get("clavicle_r_019"),
        upperarm: bonesMap.get("upperarm_r_020"),
        forearm: bonesMap.get("lowerarm_r_021"),
        hand: bonesMap.get("hand_r_022"),
        middle_eff: bonesMap.get("middle_01_r_026"),
    };
}

// ====================
// Rig loader (encapsulates GLTFLoader.load)
// ====================
export function loadRiggedArmsPerson({
    scene,
    camera,
    controls,
    solveCCD,
    logFn,
    skeletonController = null,
    applyHandOrientationConstraint = null,
    rigUrl = "./rigged_arms.glb",
    desiredHeight = 0.9,
    rigRootY = 1.0,
    onReady = null,
    onError = null,
} = {}) {
    if (!scene) throw new Error("loadRiggedArmsPerson: scene is required");
    if (!solveCCD) throw new Error("loadRiggedArmsPerson: solveCCD is required");
    if (!logFn) throw new Error("loadRiggedArmsPerson: logFn is required");

    const person = new ArmsPerson({ scene, logFn });
    // Position the whole rig root in world space.
    if (Number.isFinite(rigRootY)) {
        person.root.position.y = rigRootY;
        person.root.updateWorldMatrix(true, true);
    }
    const loader = new GLTFLoader();

    loader.load(rigUrl, (gltf) => {
        logFn("LOAD: GLB loaded");
        person.addRigScene(gltf.scene);

        gltf.scene.traverse(o => {
            o.visible = true;
            if (o.isMesh) o.frustumCulled = false;
        });

        const basic = findByName(gltf.scene, "Basiccharacter");
        if (basic) {
            basic.scale.set(1, 1, 1);
            basic.position.set(0, 0, 0);
            basic.rotation.set(0, 0, 0);
            logFn('FIX: reset "Basiccharacter"');
        }

        const skinned = findSkinnedMesh(gltf.scene);
        if (!skinned) {
            logFn("ERROR: no SkinnedMesh found");
            return;
        }

        setSkinnedMaterialNice(gltf.scene);
        const bones = cacheBones(skinned);

        const L = getLeftArmBones(bones);
        const R = getRightArmBones(bones);
        if (!L.shoulder || !L.upperarm || !L.forearm || !L.hand || !L.middle_eff) {
            logFn("ERROR: missing left bones");
            return;
        }
        if (!R.shoulder || !R.upperarm || !R.forearm || !R.hand || !R.middle_eff) {
            logFn("ERROR: missing right bones");
            return;
        }

        const fit = fitToHeight(person.rigWrap, desiredHeight);
        // Keep IK target offsets consistent with rig scaling.
        // (Offsets are in world units under person.root, not under rigWrap.)
        person.setDesiredHeight(desiredHeight);
        if (camera && controls) {
            frameCameraToBox(fit.box, { camera, controls });
        }

        person.recenterRigToShoulders(L.shoulder, R.shoulder);

        // Expose for the main script (grabbing)
        person.rightHandBoneRef = R.hand;
        person.leftHandBoneRef = L.hand;

        if (skeletonController && typeof skeletonController.setRig === "function") {
            skeletonController.setRig({
                rigRoot: gltf.scene,
                bones: skinned.skeleton.bones,
                rightHandBone: R.hand,
                leftClav: L.shoulder,
                rightClav: R.shoulder,
            });
        }

        const leftFingerMap = buildFingerMap("l", bones);
        const rightFingerMap = buildFingerMap("r", bones);

        function pickBoneByExactOrPrefix(exactName, prefix) {
            const exact = bones.get(exactName);
            if (exact) return exact;
            for (const [k, v] of bones) {
                if (k.startsWith(prefix)) return v;
            }
            return null;
        }

        // Specific joints requested for plane-mixture effectors.
        // If an exact numbered bone name changes across exports, fall back to prefix match.
        const L_planeA = pickBoneByExactOrPrefix("middle_01_l_07", "middle_01_l");
        const L_planeB = pickBoneByExactOrPrefix("ring_01_l_013", "ring_01_l");
        const L_planeC = pickBoneByExactOrPrefix("hand_l_04", "hand_l");
        const R_planeA = pickBoneByExactOrPrefix("middle_01_r_026", "middle_01_r");
        const R_planeB = pickBoneByExactOrPrefix("ring_01_r_032", "ring_01_r");
        const R_planeC = pickBoneByExactOrPrefix("hand_r_022", "hand_r");

        // Preset end-effector plane settings (per user request): centroid + small normal offset.
        // (Units are in the hand bone's local space.)
        const planeNormalOffset = 0.1;
        const fracToWrist = 0.8;
        const leftEndEffectorPlane = { weights: [fracToWrist, fracToWrist, 1], normalOffset: planeNormalOffset, normalSign: 1.0 };
        const rightEndEffectorPlane = { weights: [fracToWrist, fracToWrist, 1], normalOffset: planeNormalOffset, normalSign: 1.0 };

        person.leftArm = new Arm({
            name: "left",
            chainBones: [L.shoulder, L.upperarm, L.forearm],
            endEffectorBone: L.middle_eff,
            handBone: L.hand,
            forearmBone: L.forearm,
            bonesByNameForFingers: leftFingerMap,
            solveFn: solveCCD,
            logFn,
            scene,
            targetColor: 0x00b7ff,  // blue
            effectorColor: 0xff00ff,  // magenta
            ownerPerson: person,
            applyHandOrientationConstraint,
        });

        person.rightArm = new Arm({
            name: "right",
            chainBones: [R.shoulder, R.upperarm, R.forearm],
            endEffectorBone: R.middle_eff,
            handBone: R.hand,
            forearmBone: R.forearm,
            bonesByNameForFingers: rightFingerMap,
            solveFn: solveCCD,
            logFn,
            scene,
            targetColor: 0x00ff66,  // green
            effectorColor: 0xff00ff,  // magenta
            ownerPerson: person,
            applyHandOrientationConstraint,
        });

        // Always enable plane-mixture effectors (preset config). If joints are missing, fall back.
        if (person.leftArm) {
            if (!L_planeA || !L_planeB || !L_planeC) {
                logFn(
                    "WARN: left plane-effector joints missing; keeping default end effector bone. " +
                    `A=${!!L_planeA} B=${!!L_planeB} C=${!!L_planeC}`
                );
            } else {
                const w = leftEndEffectorPlane.weights;
                const off = leftEndEffectorPlane.normalOffset;
                const sign = leftEndEffectorPlane.normalSign;
                person.leftArm.usePlaneMixtureEndEffector({
                    jointA: L_planeA,
                    jointB: L_planeB,
                    jointC: L_planeC,
                    weights: w,
                    normalOffset: off,
                    normalSign: sign,
                    name: "left_plane_effector",
                });
            }
        }
        if (person.rightArm) {
            if (!R_planeA || !R_planeB || !R_planeC) {
                logFn(
                    "WARN: right plane-effector joints missing; keeping default end effector bone. " +
                    `A=${!!R_planeA} B=${!!R_planeB} C=${!!R_planeC}`
                );
            } else {
                const w = rightEndEffectorPlane.weights;
                const off = rightEndEffectorPlane.normalOffset;
                const sign = rightEndEffectorPlane.normalSign;
                person.rightArm.usePlaneMixtureEndEffector({
                    jointA: R_planeA,
                    jointB: R_planeB,
                    jointC: R_planeC,
                    weights: w,
                    normalOffset: off,
                    normalSign: sign,
                    name: "right_plane_effector",
                });
            }
        }

        // Attachment points for grabbed objects.
        // Prefer the arm end effector (virtual plane-mixture object) so attachments align with grasp point.
        // Fall back to the hand bone if something went wrong.
        person.rightHandAttachRef = person.rightArm?.endEffector ?? person.rightHandBoneRef;
        person.leftHandAttachRef = person.leftArm?.endEffector ?? person.leftHandBoneRef;

        person.leftArm.openHand();
        person.rightArm.openHand();

        person.leftArm.setEffectorTarget(person.offsetLocalToWorld(person.leftOffsetLocal, new THREE.Vector3()));
        person.rightArm.setEffectorTarget(person.offsetLocalToWorld(person.rightOffsetLocal, new THREE.Vector3()));

        logFn("READY: press 1 to move right hand to pickObj; press g for skeleton mode + tooltips.");
        if (onReady) onReady(person, { gltf, skinned, bones, L, R });
    }, undefined, (err) => {
        console.error(err);
        logFn("ERROR: failed to load rigged_arms.glb");
        if (onError) onError(err, person);
    });

    return person;
}

