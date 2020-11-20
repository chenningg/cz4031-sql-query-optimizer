import '../css/reset.css';
import '../css/theme.css';

import FormInput from './FormInput';

const App = () => {
  return (
    <div className="main-wrapper">
      <div className="section">
        <h1>SQL Query Optimizer</h1>
        <h3>Input an SQL query, and we'll show you the most optimized query plan.</h3>
      </div>
      <hr/>
      <div className="section">
        <FormInput/>
      </div>
    </div>
  );
}

export default App;
