import VideoComponent from "./VideoView";
import Recommendations from "@/app/[lang]/components/Recommendations";
import GraphView from "@/app/[lang]/components/GraphView";

const chartdata = [
    {
        year: 1970,
        "Export Growth Rate": 2.04,
        "Import Growth Rate": 1.53,
    },
    {
        year: 1971,
        "Export Growth Rate": 1.96,
        "Import Growth Rate": 1.58,
    },
    {
        year: 1972,
        "Export Growth Rate": 1.96,
        "Import Growth Rate": 1.61,
    },
    {
        year: 1973,
        "Export Growth Rate": 1.93,
        "Import Growth Rate": 1.61,
    },
    {
        year: 1974,
        "Export Growth Rate": 1.88,
        "Import Growth Rate": 1.67,
    },
    //...
];

function AnalysisView({dictionary, path}) {

    console.log('path', path)

    return (
        <div>
            <VideoComponent path={path} disabled={false}/>

            <h2 className='font-medium text-2xl mb-2 mt-10 dark:text-gray-100'>{dictionary['analysis']['recommendations']}</h2>
            <Recommendations dictionary={dictionary}/>

            <h2 className='font-medium text-2xl mb-2 mt-10 dark:text-gray-100'>{dictionary['analysis']['graphs']}</h2>
            <GraphView dictionary={dictionary}/>
        </div>
    )
}

export default AnalysisView