import { Fragment } from 'react'

import Table from 'react-bootstrap/Table';

import styles from "./PlanComparison.module.css";

const PlanComparison = (props) => {

  // Loads data for comparison.
  const getData = () => {
    if (props.output["error"] === false && props.output["data"].hasOwnProperty(props.planId)) {
      const planData = props.output["data"][props.planId];

      // Load in selectivities, checking for range attributes    
      const loadStats = planData["predicate_selectivity_data"].map((predicate, index) => {
        let selectivity;
        let value;

        const attribute = predicate["attribute"];
        const operator = predicate["operator"];

        if (predicate["new_selectivity"] === null) {
          selectivity = parseFloat(predicate["queried_selectivity"]).toFixed(3);
          value = predicate["queried_value"];
        }
        else {
          selectivity = parseFloat(predicate["new_selectivity"]).toFixed(3);
          value = predicate["new_value"];
        }

        return (
          <Fragment key={index}>
            <tr key={`${index}-attribute`} className={styles.attributeTableCell}>
              <td colSpan={"2"}><b>{attribute}</b></td>
            </tr>
            <tr key={`${index}-value`}>
              <td><b>Value</b></td>
              <td>{`${operator} ${value}`}</td>
            </tr>
            <tr key={`${index}-selectivity`}>
               <td><b>Selectivity</b></td>
              <td>{selectivity}</td>
            </tr>
          </Fragment>
        )
      })      

      return (
        <Table bordered hover responsive className={styles.comparisonTableWrapper}>
          <tbody>
            <tr>
              <td><b>Estimated cost per row</b></td>
              <td>{parseFloat(planData["estimated_cost_per_row"]).toFixed(3)}</td>
            </tr>
            {loadStats}
          </tbody>
        </Table>
      )
    }
    else {
      return null;
    }
  }

  return (
    props.output["data"].hasOwnProperty(props.planId) ?
    <div>
      {getData()}
    </div> :
    <div className={styles.comparisonLoadingWrapper}>
      <span>No data to show</span>
    </div>
  )
}

export default PlanComparison;