import Table from 'react-bootstrap/Table';

import styles from "./PlanComparison.module.css";

const PlanComparison = (props) => {

  // Loads data for comparison.
  const getData = () => {
    if (props.output["error"] === false && props.output["data"].hasOwnProperty(props.planId)) {
      return (
        <Table striped bordered hover className={styles.comparisonTableWrapper}>
          <thead>
            <tr>
              <th>Testing</th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Username</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Test</td>
              <td>Test</td>
              <td>Test</td>
              <td>Test</td>
            </tr>
          </tbody>
        </Table>
      )
    }
    else {
      return null;
    }
  }

  return (
    getData() !== null ?
    <div>
      {getData()}
    </div> :
    <div className={styles.comparisonLoadingWrapper}>
      <span>Waiting for data...</span>
    </div>
  )
}

export default PlanComparison;