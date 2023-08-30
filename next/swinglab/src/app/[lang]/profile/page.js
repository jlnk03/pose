import {getDictionary} from '@/get-dictionary'


async function App({params: {lang}}) {

    const dictionary = await getDictionary(lang)

    return (
        <>
            <span>
                Profile
            </span>
            {/* <NavigationMenuBar dictionary={dictionary} /> */}
        </>
    );
}

export default App;