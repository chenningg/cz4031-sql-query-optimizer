import Container from 'react-bootstrap/Container';
import FormInput from '../FormInput/FormInput';

import styles from "./App.module.css";

const App = () => {
  return (
    <Container fluid="md">
      <div className={styles.headerWrapper}>
        <h1>SQL Query Optimizer</h1>
        <p className="lead">Input an SQL query to compare various execution plans.</p>
        <p className={styles.headerText}>Welcome! Enter a properly formatted SQL query on the right. The query must be based on the <a href="http://www.tpc.org/tpch/" target="_blank" rel="noopener noreferrer">TPC-H</a> dataset, and requires a database set up according to <a href="https://github.com/chenningg/sql-query-optimizer#setting-up-postgresql-and-the-tpc-h-dataset" target="_blank" rel="noopener noreferrer">these</a> instructions. You can also select predicates to vary on the left, which will allow the DBMS (Postgresql) to vary the selectivity of those predicates to find alternate plans for comparison.</p>
        <p className={styles.headerText}>Only allowable predicates have been added to the list, so don't be surprised if some attributes are missing! Allowable predicates include numeric and date attributes, and these predicates must each have a histogram available in the database.</p>
      </div>
      <hr/>
      <FormInput/>
    </Container>
  );
}

export default App;
