'use client'

import React, {useEffect, useRef, useState} from 'react';
import {Card} from '@tremor/react';

function ReportFocusView({id1, id2, text}) {
    return (
        <div className="flex flex-col justify-end w-full h-full gap-4">
            <div
                className="flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2 items-center">
                <span
                    className="h-8 w-8 text-center flex-none flex items-center justify-center text-gray-500 font-bold text-xl">1</span>
                <span id={id1} className="flex justify-center items-center"></span>

                <span>
                    {text[0]}
                </span>
            </div>

            <div className="flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-2 gap-2">
                <span
                    className="h-8 w-8 text-center flex-none flex items-center justify-center text-gray-500 font-bold text-xl">2</span>
                <span id={id2} className="flex justify-center items-center"></span>
                <span>
                    {text[1]}
                </span>
            </div>
        </div>
    );
}


function DotsIndicator({total, activeIndex}) {
    return (
        <div className="flex justify-center space-x-2 absolute bottom-2 left-1/2 -translate-x-1/2">
            {Array.from({length: total}).map((_, index) => (
                <span
                    key={index}
                    className={`h-2 w-2 rounded-full ${index === activeIndex ? 'bg-red-500' : 'bg-gray-400'}`}
                ></span>
            ))}
        </div>
    );
}

function ReportSummary({position, dictionary, text}) {
    const reportContainers = ['focus', 'hips', 'shoulders'];
    const [activeIndex, setActiveIndex] = useState(0);
    const scrollContainerRef = useRef(null);
    // const canvasRef = useRef(null);

    const handleScroll = () => {
        if (!scrollContainerRef.current) return;

        const containerWidth = scrollContainerRef.current.offsetWidth;
        const childWidth = scrollContainerRef.current.children[0].offsetWidth;
        const scrollPosition = scrollContainerRef.current.scrollLeft;
        const activeIdx = Math.floor(scrollPosition / childWidth);

        setActiveIndex(activeIdx);
    };

    useEffect(() => {
        const container = scrollContainerRef.current;
        if (container) {
            container.addEventListener('scroll', handleScroll);
        }

        return () => {
            if (container) {
                container.removeEventListener('scroll', handleScroll);
            }
        };
    }, []);


    return (
        <div className="flex flex-col relative mt-14">
            {/*<canvas ref={canvasRef}*/}
            {/*        className="rounded-2xl max-h-40 max-w-24 bg-gray-200 dark:bg-gray-800 absolute top-0 right-0 z-30 transform -translate-x-1/2 -translate-y-1/4"></canvas>*/}
            {/*<img src="assets/page_dots.png" className="absolute bottom-0 right-1/2 transform translate-x-1/2 z-20 h-10 w-10" alt="Page Dots" />*/}
            <span
                className="sm:text-xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1">{position.charAt(0).toUpperCase() + position.slice(1)}</span>

            <Card>
                <div id="impact_report" ref={scrollContainerRef}
                     className={`flex flex-row h-60 gap-4 overflow-x-auto snap-x snap-mandatory w-full relative hide-scrollbar`}>
                    {reportContainers.map((container, index) => (
                        <div
                            key={index}
                            className="flex flex-col w-full flex-none snap-start">
                            <span
                                className="sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2">{dictionary['analysis']['bodyParts'][index]}</span>
                            <ReportFocusView
                                id1={`${container}_report_text_${position}_1`}
                                id2={`${container}_report_text_${position}_2`}
                                text={text[container]}
                            />
                        </div>
                    ))}

                </div>
            </Card>

            <DotsIndicator total={3} activeIndex={activeIndex}/>

        </div>
    );
}

export default ReportSummary;

