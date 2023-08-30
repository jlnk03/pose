import '../../globals.css'
import '../../tailwind.css'
import '../../style.css'
import {i18n} from '@/i18n-config'

export async function generateStaticParams() {
    return i18n.locales.map((locale) => ({lang: locale}))
}


export const metadata = {
    title: 'Swinglab',
    description: '3D Swing analysis coach',
}

export default function RootLayout({children, params}) {
    return (

        <html lang={params.lang}>
        <body className='text-black dark:text-gray-100'>
        {children}
        </body>
        </html>

    )
}
