export default function manifest() {
    return {
        name: 'Swinglab',
        short_name: 'Swinglab',
        description: '3D Swing analysis coach',
        start_url: '/',
        display: 'standalone',
        background_color: '#fff',
        theme_color: '#fff',
        icons: [
            {
                src: '/assets/favicon.png',
                sizes: 'any',
            },
        ],
    }
}