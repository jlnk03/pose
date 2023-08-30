'use client'

import {useState} from 'react'
import {Tab} from '@headlessui/react'
import {usePositionVideoStorage} from '@/app/context/storage'

function classNames(...classes) {
    return classes.filter(Boolean).join(' ')
}

export default function PositionSelection({skipToPercentage}) {
    let [categories] = useState({
        Setup: [
            {
                id: 1,
                title: 'Does drinking coffee make you smarter?',
                date: '5h ago',
                commentCount: 5,
                shareCount: 2,
            },
            {
                id: 2,
                title: "So you've bought coffee... now what?",
                date: '2h ago',
                commentCount: 3,
                shareCount: 2,
            },
        ],
        Top: [
            {
                id: 1,
                title: 'Is tech making coffee better or worse?',
                date: 'Jan 7',
                commentCount: 29,
                shareCount: 16,
            },
            {
                id: 2,
                title: 'The most innovative things happening in coffee',
                date: 'Mar 19',
                commentCount: 24,
                shareCount: 12,
            },
        ],
        Impact: [
            {
                id: 1,
                title: 'Ask Me Anything: 10 answers to your questions about coffee',
                date: '2d ago',
                commentCount: 9,
                shareCount: 5,
            },
            {
                id: 2,
                title: "The worst advice we've ever heard about coffee",
                date: '4d ago',
                commentCount: 1,
                shareCount: 2,
            },
        ],
        Finish: []
    })

    const {positionVideo, setPositionVideo} = usePositionVideoStorage()

    return (
        <div className="w-full px-2 sm:px-0">
            <Tab.Group
                onChange={(index) => {
                    skipToPercentage(positionVideo[index])
                }
                }
            >
                <Tab.List className="flex space-x-1 rounded-full bg-blue-900/20 dark:bg-blue-800/60 p-1">
                    {Object.keys(categories).map((category) => (
                        <Tab
                            key={category}
                            className={({selected}) =>
                                classNames(
                                    'w-full rounded-full py-1.5 text-sm font-medium leading-5 text-blue-700 dark:text-blue-200',
                                    ' focus:outline-none',
                                    selected
                                        ? 'bg-white dark:bg-blue-700/50 shadow'
                                        : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
                                )
                            }
                        >
                            {category}
                        </Tab>
                    ))}
                </Tab.List>
            </Tab.Group>
        </div>
    )
}
