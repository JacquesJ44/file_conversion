import { BrowserRouter, Routes, Route } from 'react-router-dom';

import './App.css';
import Home from './Home';

function App() {
  return (
    <BrowserRouter>
      <div className="App-header">
        <div className='content flex justify-center'>
              <Routes>
                <Route path='/' element={<Home />} />
              </Routes>
            </div> 
      </div>
    </BrowserRouter>
  );
}

export default App;
