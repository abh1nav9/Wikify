import { RouterProvider } from 'react-router-dom';
import Router from './Routes/Index';

function App() {
  return (
    <>
    <RouterProvider router={Router}/>
    </>
  )
}

export default App;