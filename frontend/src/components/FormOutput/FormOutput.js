import { useState } from "react";

import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';

import QueryVisualizer from "../QueryVisualizer/QueryVisualizer";

import styles from "./FormOutput.module.css";

const FormOutput = (props) => {

  const [planSelected, setPlanSelected] = useState([0, 1])

  // Render alternative plan selection
  const renderAlternativeSelector = () => {
    if (props.output["error"] === false && JSON.stringify(props.output["data"]) !== JSON.stringify({})) {
      return (
        Object.keys(props.output["data"]).map((key) => {
          if (key === 0 || key === "0") {
            return (
              <option key={key} value={key}>Original plan</option>
            )
          }
          else {
            return (
              <option key={key} value={key}>Alternative plan {key}</option>
            )
          }
        })
      );
    }
    else {
      return <option>No plans available</option>;
    }
  }

  // Changes which plan is selected to compare
  const handleSelect = (planId, event) => {
    if (planId === 0) {
      setPlanSelected((oldState) => {
        let newState = [...oldState];
        newState[0] = event.target.value;
        return (newState);
      })
    }
    else {
      setPlanSelected((oldState) => {
        let newState = [...oldState];
        newState[1] = event.target.value;
        return (newState);
      })
    }
  }

  const parseExplanation = (planId) => {
    if (props.output["error"] === false && props.output["data"].hasOwnProperty(planId)) {
      return (
        <ol>
          {props.output["data"][planId]["explanation"].map((step, index) => {
            return (
              <li key={index}>{step}</li>
            )
          })}
        </ol >
      );
    }
    else {
      return (
        <div className={styles.explanationLoadingWrapper}>Waiting for data...</div>
      );
    }
  }

  return (
    <>
      <Form.Row>
        <h1>Compare plans</h1>
      </Form.Row>
      <Form.Row>
        <Form.Group as={Col} controlId="formPlanSelector1">
          <Form.Label><b>Select plan:</b></Form.Label>
          <Form.Control as="select" value={planSelected[0]} onChange={(event) => {handleSelect(0, event)}}>
            {renderAlternativeSelector()}
          </Form.Control>
        </Form.Group>
        <Form.Group as={Col} controlId="formPlanSelector2">
          <Form.Label><b>Select plan:</b></Form.Label>
          <Form.Control as="select" value={planSelected[1]} onChange={(event) => {handleSelect(1, event)}}>
            {renderAlternativeSelector()}
          </Form.Control>
        </Form.Group>
      </Form.Row>
      <Form.Row>
        <Form.Group as={Col} controlId="formGraph1">
          <QueryVisualizer output={props.output} planId={planSelected[0]}/>
        </Form.Group>
        <Form.Group as={Col} controlId="formGraph2">
          <QueryVisualizer output={props.output} planId={planSelected[1]}/>
        </Form.Group>
      </Form.Row>
      
      <Form.Row>
        <Form.Group as={Col} controlId="formExplanation1">
          <div className={styles.explanationWrapper} >
            {parseExplanation(planSelected[0])}
          </div>
        </Form.Group>
        <Form.Group as={Col} controlId="formExplanation2">
          <div className={styles.explanationWrapper} >
            {parseExplanation(planSelected[1])}
          </div>
        </Form.Group>
      </Form.Row>
    </>
  )
}

export default FormOutput;