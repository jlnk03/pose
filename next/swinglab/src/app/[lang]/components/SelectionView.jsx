'use client'

import React, {useState} from 'react';
// import { Button, Input } from 'antd';
// import { CloseOutlined } from '@ant-design/icons';

const SelectionView = () => {
    const [showSelectionView, setShowSelectionView] = useState(false);
    const [newMargins, setNewMargins] = useState({
        setup: {low: '', high: ''},
        top: {low: '', high: ''},
        impact: {low: '', high: ''},
    });

    const handleDismissSelectionView = () => {
        setShowSelectionView(false);
    };

    const handleOpenSelectionView = () => {
        setShowSelectionView(true);
    };

    const handleInputChange = (e, category, type) => {
        setNewMargins((prevState) => ({
            ...prevState,
            [category]: {
                ...prevState[category],
                [type]: e.target.value,
            },
        }));
    };

    const handleSubmitNewMargins = () => {
        // Handle submit logic
    };

    return (
        <>
            {/* Selection View background dismiss button */}
            <button
                id="selection-view-dismiss"
                className={`fixed w-full h-full top-0 left-0 z-20 bg-black bg-opacity-50 backdrop-filter backdrop-blur-sm ${
                    showSelectionView ? '' : 'hidden'
                }`}
                onClick={handleDismissSelectionView}
            />

            {/* Selection view in center of screen */}
            <div
                id="selection-view"
                className={`${
                    showSelectionView ? '' : 'hidden'
                } fixed flex flex-col px-4 pt-14 pb-4 w-96 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-2xl shadow-lg z-30`}
            >
                <div
                    id="new_margins_title"
                    className="w-fit text-lg font-medium text-slate-900 dark:text-gray-100 pt-4 absolute top-6 transform -translate-x-1/2 left-1/2"
                >
                    New margins
                </div>

                <div
                    className="relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-4 flex flex-row">
                    Setup
                </div>
                <div className="flex flex-row gap-2">
                    <input
                        id="setup_low_new_margins"
                        type="number"
                        className="dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm"
                        value={newMargins.setup.low}
                        onChange={(e) => handleInputChange(e, 'setup', 'low')}
                    />
                    <input
                        id="setup_high_new_margins"
                        type="number"
                        className="dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm"
                        value={newMargins.setup.high}
                        onChange={(e) => handleInputChange(e, 'setup', 'high')}
                    />
                </div>

                <div
                    className="relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-2 flex flex-row">
                    Top
                </div>
                <div className="flex flex-row gap-2">
                    <input
                        id="top_low_new_margins"
                        type="number"
                        className="dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm"
                        value={newMargins.top.low}
                        onChange={(e) => handleInputChange(e, 'top', 'low')}
                    />
                    <input
                        id="top_high_new_margins"
                        type="number"
                        className="dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm"
                        value={newMargins.top.high}
                        onChange={(e) => handleInputChange(e, 'top', 'high')}
                    />
                </div>

                <div
                    className="relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-2 flex flex-row">
                    Impact
                </div>
                <div className="flex flex-row gap-2">
                    <input
                        id="impact_low_new_margins"
                        type="number"
                        className="dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm"
                        value={newMargins.impact.low}
                        onChange={(e) => handleInputChange(e, 'impact', 'low')}
                    />
                    <input
                        id="impact_high_new_margins"
                        type="number"
                        className="dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm"
                        value={newMargins.impact.high}
                        onChange={(e) => handleInputChange(e, 'impact', 'high')}
                    />
                </div>

                <button
                    id="submit-new-margins"
                    className="relative justify-start text-sm font-medium text-gray-100 flex flex-row bg-indigo-500 hover:bg-indigo-600 rounded-lg items-center justify-center px-4 py-2 mt-2 w-fit"
                    onClick={handleSubmitNewMargins}
                >
                    Save
                </button>
            </div>

            {/* End selection view */}
        </>
    );
};

export default SelectionView;