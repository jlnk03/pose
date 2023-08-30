'use client'
import {useReplicateStorage} from "../../context/storage";
import LinePlot from "@/app/[lang]/components/LinePlot";

function GraphView({dictionary}) {
    const {replicateOut, setReplicateOut} = useReplicateStorage();

    if (replicateOut.length === 0) {
        return null
    }

    // console.log('replicateOut', replicateOut)
    // console.log('replicateOut[0]', replicateOut['angles'])
    // console.log('replicateOut[0]', replicateOut['angles'][0])


    return (
        <>
            <div className="flex flex-col gap-5 mb-5">
                <LinePlot yValues={replicateOut['angles'][0]} title={dictionary['metrics']['hipRotation']}/>
                <LinePlot yValues={replicateOut['angles'][1]} title={dictionary['metrics']['hipTilt']}/>
                <LinePlot yValues={replicateOut['angles'][5]} title={dictionary['metrics']['shoulderRotation']}/>
                <LinePlot yValues={replicateOut['angles'][6]} title={dictionary['metrics']['shoulderBend']}/>
                <LinePlot yValues={replicateOut['angles'][7]} title={dictionary['metrics']['shoulderTilt']}/>
            </div>
        </>
    )
}

export default GraphView