"use client"

import * as React from "react"
import Link from "next/link"
// import { Icons } from "@/components/icons"
import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"


export function NavigationMenuBar({dictionary}) {

    return (
        <NavigationMenu
            className='absolute top-5 left-1/2 -translate-x-1/2 border-gray-200 border p-1 rounded-lg shadow-sm'>
            <NavigationMenuList>
                <NavigationMenuItem>
                    <Link href="/">
                        <NavigationMenuLink className={navigationMenuTriggerStyle()} legacyBehavior passHref>
                            {dictionary['navigation']['home']}
                        </NavigationMenuLink>
                    </Link>
                </NavigationMenuItem>
                <NavigationMenuItem>
                    <Link href="/profile">
                        <NavigationMenuLink className={navigationMenuTriggerStyle()} legacyBehavior passHref>
                            {dictionary['navigation']['profile']}
                        </NavigationMenuLink>
                    </Link>
                </NavigationMenuItem>
                <NavigationMenuItem>
                    <Link
                        href={{
                            pathname: '/dashboard',
                            query: {videoId: '1'},
                        }}
                    >
                        <NavigationMenuLink className={navigationMenuTriggerStyle()} legacyBehavior passHref>
                            {dictionary['navigation']['dashboard']}
                        </NavigationMenuLink>
                    </Link>
                </NavigationMenuItem>
            </NavigationMenuList>
        </NavigationMenu>
    )
}
