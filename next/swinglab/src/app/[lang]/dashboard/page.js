import Dashboard from "../components/Dashboard";
import {getDictionary} from '@/get-dictionary'
import Navbar from '../components/Navbar';


async function App({params: {lang}}) {

    const dictionary = await getDictionary(lang)

    return (
        <>
            <Navbar dictionary={dictionary} lang={lang}>
            </Navbar>

            <Dashboard dictionary={dictionary}/>
        </>
    );
}

export default App;