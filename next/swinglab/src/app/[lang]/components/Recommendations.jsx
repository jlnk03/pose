'use client'

import ReportSummary from "@/app/[lang]/components/ReportFocusView";
import {usePositionVideoStorage, useReplicateStorage} from "../../context/storage";


function Recommendations({dictionary}) {

    const {replicateOut, setReplicateOut} = useReplicateStorage();
    const {positionVideo, setPositionVideo} = usePositionVideoStorage();

    if (replicateOut.length === 0) {
        return null
    }

    // get position of impact, top and setup in video and multiply by length of angles array
    let impactPos = positionVideo[2] * replicateOut['angles'][0].length
    let topPos = positionVideo[1] * replicateOut['angles'][0].length
    let setupPos = positionVideo[0] * replicateOut['angles'][0].length

    // round to nearest integer
    impactPos = Math.round(impactPos)
    topPos = Math.round(topPos)
    setupPos = Math.round(setupPos)

    const impactHipsRot = replicateOut['angles'][0][impactPos]
    const impactHipsTilt = replicateOut['angles'][1][impactPos]
    const topHipsRot = replicateOut['angles'][0][topPos]
    const topHipsTilt = replicateOut['angles'][1][topPos]
    const setupHipsRot = replicateOut['angles'][0][setupPos]
    const setupHipsTilt = replicateOut['angles'][1][setupPos]

    const impactShoulderRot = replicateOut['angles'][2][impactPos]
    const impactShoulderTilt = replicateOut['angles'][3][impactPos]
    const topShoulderRot = replicateOut['angles'][2][topPos]
    const topShoulderTilt = replicateOut['angles'][3][topPos]
    const setupShoulderRot = replicateOut['angles'][2][setupPos]
    const setupShoulderTilt = replicateOut['angles'][3][setupPos]

    const hipsSetupText = rotationText(setupHipsRot, [-10, 10], 'hips')
    const hipsTopText = rotationText(topHipsRot, [-10, 10], 'hips')
    const hipsImpactText = rotationTextDown(impactHipsRot, [-10, 10], 'hips')

    const hipsSetupTiltText = tiltText(setupHipsTilt, [-10, 10], 'hips')
    const hipsTopTiltText = tiltText(topHipsTilt, [-10, 10], 'hips')
    const hipsImpactTiltText = tiltText(impactHipsTilt, [-10, 10], 'hips')

    const shoulderSetupText = rotationText(setupShoulderRot, [-10, 10], 'shoulders')
    const shoulderTopText = rotationText(topShoulderRot, [-10, 10], 'shoulders')
    const shoulderImpactText = rotationTextDown(impactShoulderRot, [-10, 10], 'shoulders')

    const shoulderSetupTiltText = tiltText(setupShoulderTilt, [-10, 10], 'shoulders')
    const shoulderTopTiltText = tiltText(topShoulderTilt, [-10, 10], 'shoulders')
    const shoulderImpactTiltText = tiltText(impactShoulderTilt, [-10, 10], 'shoulders')

    const focusSetup = getFocus([hipsSetupText, hipsSetupTiltText, shoulderSetupText, shoulderSetupTiltText])
    const focusTop = getFocus([hipsTopText, hipsTopTiltText, shoulderTopText, shoulderTopTiltText])
    const focusImpact = getFocus([hipsImpactText, hipsImpactTiltText, shoulderImpactText, shoulderImpactTiltText])

    const setupTextArray = {
        'focus': focusSetup,
        'hips': [hipsSetupText[1], hipsSetupTiltText[1]],
        'shoulders': [shoulderSetupText[1], shoulderSetupTiltText[1]]
    }
    const topTextArray = {
        'focus': focusTop,
        'hips': [hipsTopText[1], hipsTopTiltText[1]],
        'shoulders': [shoulderTopText[1], shoulderTopTiltText[1]]
    }
    const impactTextArray = {
        'focus': focusImpact,
        'hips': [hipsImpactText[1], hipsImpactTiltText[1]],
        'shoulders': [shoulderImpactText[1], shoulderImpactTiltText[1]]
    }


    function rotationText(angle, margin, body_part) {
        if (angle < margin[0]) {
            const text = `Rotate your ${body_part} a little less to the right.`
            return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else if (angle > margin[1]) {
            const text = `Rotate your ${body_part} a little more to the right.`
            return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else {
            body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
            const text = `${body_part} rotation: 👍`
            return [0, text]
        }
    }

    function rotationTextDown(angle, margin, body_part) {
        if (angle < margin[0]) {
            const text = `Rotate your ${body_part} a little more to the left.`
            return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else if (angle > margin[1]) {
            const text = `Rotate your ${body_part} a little less to the left.`
            return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else {
            body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
            const text = `${body_part} rotation: 👍`
            return [0, text]
        }
    }

    function tiltText(angle, margin, body_part) {
        if (angle < margin[0]) {
            const text = `Tilt your ${body_part} a little less to the right.`
            return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else if (angle > margin[1]) {
            const text = `Tilt your ${body_part} a little more to the right.`
            return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else {
            body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
            const text = `${body_part} tilt: 👍`
            return [0, text]
        }
    }


    function bendText(angle, margin, body_part) {
        if (angle < margin[0]) {
            const text = `Bend your ${body_part} a little more forward.`
            return [Math.abs(margin[0] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else if (angle > margin[1]) {
            const text = `Bend your ${body_part} a little less forward.`
            return [Math.abs(margin[1] - angle) / Math.abs(margin[0] - margin[1]), text]
        } else {
            body_part = body_part.charAt(0).toUpperCase() + body_part.slice(1)
            const text = `${body_part} bend: 👍`
            return [0, text]
        }
    }

    function getFocus(errorArray) {
        //     sort the array
        errorArray.sort((a, b) => b[0] - a[0]);
        //     get the first two elements
        return [errorArray[0][1], errorArray[1][1], errorArray[2][1]];
    }

    const [impactHipsRotScore, impactHipsRotText] = rotationTextDown(impactHipsRot, [-10, 10], 'hips')
    const [impactHipsTiltScore, impactHipsTiltText] = rotationTextDown(impactHipsTilt, [-10, 10], 'hips')

    return (
        <div className='mb-5 grid sm:grid-cols-2 grid-cols-1 gap-3'>
            <ReportSummary position={'setup'} dictionary={dictionary} text={setupTextArray}/>
            <ReportSummary position={'top'} dictionary={dictionary} text={topTextArray}/>
            <ReportSummary position={'impact'} dictionary={dictionary} text={impactTextArray}/>
        </div>
    )
}

export default Recommendations