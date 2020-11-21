import { useState, useEffect } from 'react';

const FormInput = () => {
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    fetch('/time').then(res => res.json()).then(data => {
      setCurrentTime(data.time);
    });
  }, []);

  return (
    <div className="flex">
      <div className="flex-item">
        <h2>SQL query</h2>
        <textarea placeholder="Input SQL query..."></textarea>
        <button>Generate</button>
      </div>
      <div className="flex-item">
        <h2>Output</h2>
        <textarea readOnly></textarea>
        <button>Toggle</button>
      </div>
    </div>)
}
      
export default FormInput;