import Container from 'react-bootstrap/Container'
import FormInput from '../FormInput/FormInput';

const App = () => {
  return (
    <Container fluid="md">
      <div className="text-center">
        <h1>SQL Query Optimizer</h1>
        <p className="lead">Input an SQL query, and we'll show you the most optimized query plan.</p>
      </div>
      <hr/>
      <FormInput/>
    </Container>
  );
}

export default App;
