'use client'

import {Card} from '@tremor/react';
import UploadSide from './UploadSide';


function UploadComponent({dictionary}) {

    return (
        <Card
            className="relative flex items-start justify-center text-center flex-col sm:w-2/3 sm:h-2/3 w-[90%] h-[90%]">
            <div className="flex flex-col items-start mb-4">
                <span className="text-3xl font-bold text-slate-900 dark:text-gray-100">
                    {dictionary['upload-video']}
                </span>
                <span className="text-sm font-medium text-slate-900 dark:text-gray-100">
                    mp4, mov, avi – max. 20 MB
                </span>
            </div>
            <UploadSide dictionary={dictionary} className='w-full h-full' textSize='text-3xl' svgSize='3em'
                        tiltAngle={3}/>
        </Card>
    );
}

export default UploadComponent;