import { useState } from 'react';
import axios from "axios";

import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Accordion from 'react-bootstrap/Accordion'
import Card from 'react-bootstrap/Card'
import Toast from 'react-bootstrap/Toast'
import Spinner from 'react-bootstrap/Spinner'

import FormOutput from "../FormOutput/FormOutput";

import styles from "./FormInput.module.css";

const FormInput = () => {
  const [input, setInput] = useState({
    "query": "",
    "predicates": []
  });
  const [output, setOutput] = useState({
    "data": {},
    "bestPlanId": 1,
    "status": "",
    "error": false
  });

  const [showPredicateWarning, setShowPredicateWarning] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();
    setShowLoading(true);
    setOutput((oldState) => {
      return (
        {...oldState, "status": "Generating output...", "error": false}
      )
    })

    if (input.query !== "") {
      axios.post("/generate", input)
        .then((response) => {
          setShowLoading(false);
          // Handle error gracefully
          if (response.status === false || response.data["error"] === true) {
            setOutput((oldState) => { 
              return (
                {...oldState, "status": response.data["status"], "error": true}
              )
            })
            setShowError(true);
          }
          else {
            console.log(response.data);
            setOutput((oldState) => { 
              return (
                {...oldState, "data": response.data["data"], "bestPlanId": response.data["best_plan_id"], "status": response.data["status"], "error": false}
              )
            })
            setShowSuccess(true);
          }
      })
      .catch((error) => {
        setShowLoading(false);
        setOutput((oldState) => { 
          return (
            {...oldState, "status": "Error generating output. Please check your query's formatting and/or validity.", "error": true}
          )
        })
        setShowError(true);
      })
    }
    else {
      setShowLoading(false);
      setOutput((oldState) => { 
        return (
          {...oldState, "status": "Error generating output. Please input an SQL query.", "error": true}
        )
      })
      setShowError(true);
    }
  }

  const limitPredicates = (event) => {
    // let timeout;
    // if (typeof(timeout) !== undefined) {
    //   setTimeout(() => { setAlert(false); }, 2000);
    //   setAlert(true);
    // }

    event.target.checked = false;
    setShowPredicateWarning(true);
  }

  // Handles user's adding of predicates, and limits them if it goes above 4 predicates.
  const handleChecked = (event) => {
    setInput(oldState => {
      const index = oldState.predicates.indexOf(event.target.id);

      if (event.target.checked) {
        if (index <= -1) {
          // If too many, stop user from choosing more.
          if (oldState.predicates.length >= 4) {
            limitPredicates(event);
            return (oldState);
          }
          oldState.predicates.push(event.target.id)
        }
      }
      else {
        if (index > -1) {
          oldState.predicates.splice(index, 1);
        }
      }

      return ({ ...oldState, "predicates": oldState.predicates });
    });
  }

  const resetForm = (event) => {
    setInput({
      "query": "",
      "predicates": []
    });
    setOutput({
      "data": {},
      "best_plan_id": 1,
      "status": "",
      "error": false
    });
  }

  const showSelectedPredicates = () => {
    if (input.predicates && input.predicates.length > 0) {
      let selectedPredicates = "";
      input.predicates.forEach((predicate) => {
        selectedPredicates += `${predicate}, `
      })
      return (selectedPredicates.slice(0, selectedPredicates.length-2));
    }
    else {
      return "";
    }
  }

  return (
    <>
      {
        <>
          <div className={styles.toastWrapper}>
            <Toast bsPrefix={styles.toastError} animation={true} autohide={true} delay={3000} onClose={() => {setShowPredicateWarning(false)}} show={showPredicateWarning}>
              <Toast.Header bsPrefix={styles.toastHeader}>Too many predicates!</Toast.Header>
              <Toast.Body bsPrefix={styles.toastBody}>You may not select more than 4 predicates.</Toast.Body>
            </Toast>
          </div>

          <div className={styles.toastWrapper}>
            <Toast bsPrefix={styles.toastLoading} animation={true} autohide={false} delay={3000} onClose={() => {setShowLoading(false)}} show={showLoading}>
              <Spinner animation="border" size="sm" variant="light" as="span" role="status"></Spinner>
              <Toast.Header bsPrefix={styles.toastHeader}>Loading data...</Toast.Header>
            </Toast>
          </div>

          <div className={styles.toastWrapper}>
            <Toast bsPrefix={styles.toastSuccess} animation={true} autohide={true} delay={3000} onClose={() => {setShowSuccess(false)}} show={showSuccess}>
              <Toast.Header bsPrefix={styles.toastHeader}>Success!</Toast.Header>
              <Toast.Body bsPrefix={styles.toastBody}>Data loaded. Please see the output for the results.</Toast.Body>
            </Toast>
          </div>

          <div className={styles.toastWrapper}>
            <Toast bsPrefix={styles.toastError} animation={true} autohide={true} delay={8000} onClose={() => {setShowError(false)}} show={showError}>
              <Toast.Header bsPrefix={styles.toastHeader}>Error!</Toast.Header>
              <Toast.Body bsPrefix={styles.toastBody}>{output.status}</Toast.Body>
            </Toast>
          </div>
        </>
      }
      
      <Form onSubmit={handleSubmit} className="mb-4">
        <Form.Row>
          <Form.Group as={Col} controlId="formPredicatesInput">
            <Form.Label>Selected predicates</Form.Label>
            <Form.Control value={showSelectedPredicates()} readOnly />
          </Form.Group>
        </Form.Row>

        <Form.Row>
          <Form.Group as={Col} controlId="formPredicates">
            <Form.Label>Predicates</Form.Label>
            <Form.Text>Select up to 4 predicates that are limited by a range condition in a WHERE clause in the query (no equality conditions). For example, <i><b>WHERE attribute_name &gt; 100</b></i></Form.Text>
            <Accordion>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="0">
                  Region
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="0">
                  <Card.Body>
                    {["r_regionkey"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="1">
                  Nation
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="1">
                  <Card.Body>
                    {["n_nationkey"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="2">
                  Supplier
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="2">
                  <Card.Body>
                    {["s_suppkey", "s_acctbal"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="3">
                  Customer
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="3">
                  <Card.Body>
                    {["c_custkey", "c_acctbal"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="4">
                  Part
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="4">
                  <Card.Body>
                    {["p_partkey", "p_retailprice"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="5">
                  PartSupp
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="5">
                  <Card.Body>
                    {["ps_partkey", "ps_suppkey", "ps_availqty", "ps_supplycost"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="6">
                  Orders
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="6">
                  <Card.Body>
                    {["o_orderkey", "o_custkey", "o_totalprice", "o_orderdate"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
              <Card>
                <Accordion.Toggle as={Card.Header} variant="link" eventKey="7">
                  LineItem
                </Accordion.Toggle>
                <Accordion.Collapse eventKey="7">
                  <Card.Body>
                    {["l_orderkey", "l_partkey", "l_suppkey", "l_extendedprice", "l_shipdate", "l_commitdate", "l_receiptdate"].map((type) => (
                      <Form.Check
                        type="checkbox" key={type} id={type} label={type} onClick={handleChecked} />
                    ))}
                  </Card.Body>
                </Accordion.Collapse>
              </Card>
            </Accordion>
          </Form.Group>

          <Form.Group as={Col} controlId="formInput">
            <Form.Group controlId="formQuery">
                <Form.Label>SQL Query</Form.Label>
                <Form.Text>Please input your SQL query. Ensure that the query is properly formatted. Please leave a space between every operator. For example, <i><b>attribute &gt; 5</b></i> instead of <i><b>attribute&gt;5</b></i></Form.Text>
                <Form.Control as="textarea" rows="19" placeholder="Input SQL query..." onChange={event => setInput({...input, "query": event.target.value})} value={input.query} />
              <Row>
                <Col>
                  <Button onClick={ resetForm } variant="secondary" type="reset" className="w-100 mt-3">
                  Reset
                  </Button>
                </Col>
                <Col>
                  <Button variant="primary" type="submit" className="w-100 mt-3">
                  Generate
                  </Button>
                </Col>
              </Row>
            </Form.Group>
          </Form.Group>
        </Form.Row>
      </Form>

      <FormOutput output={output}/>
    </>
  )
}
      
export default FormInput;