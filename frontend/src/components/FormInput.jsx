import { useState } from 'react';
import axios from "axios";

const FormInput = () => {
  const [query, setQuery] = useState("");
  const [output, setOutput] = useState("");

  const handleChange = (event) => {
    setQuery(event.target.value);
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    setOutput("Generating output...")

    axios.post("/test", {
      query: query,
    })
    .then((response) => {
      setOutput(response.data);
    })
    .catch((error) => {
      setOutput(error);
    })
  }

  return (
    <div className="flex">
      <div className="flex-item">
        <form onSubmit={handleSubmit}>
          <h2>SQL query</h2>
          <textarea placeholder="Input SQL query..." onChange={handleChange} value={query}></textarea>
          <button type="submit">Generate</button>
        </form>
      </div>
      <div className="flex-item">
        <h2>Output</h2>
        <textarea readOnly value={output}></textarea>
        <button>Toggle</button>
      </div>
    </div>)
}
      
export default FormInput;