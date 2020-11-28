import { useState } from 'react';
import axios from "axios";

import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Accordion from 'react-bootstrap/Accordion'
import Card from 'react-bootstrap/Card'

import FormOutput from "./FormOutput";

const FormInput = () => {
  const [input, setInput] = useState({
    "query": "",
    "predicates": [],
    "selectivity": 50,
  });
  const [output, setOutput] = useState({
    "plans": 0,
    "output": "",
    "explanation": [],
  });

  const [showAlert, setAlert] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();
    setOutput("Generating output...")

    if (input.query !== "") {
      axios.post("/generate", input)
        .then((response) => {
          setOutput({ "output": response.data.output, "explanation": response.data.explanation });
          console.log(output);
      })
      .catch((error) => {
        setOutput({ ...output, "output": "ERROR: Please ensure that your SQL query is executable." });
      })
    }
    else {
      setOutput({ ...output, "output": "ERROR: Please input an SQL query."});
    }
  }

  const limitPredicates = (event) => {
    let timeout;
    if (typeof(timeout) !== undefined) {
      setTimeout(() => { setAlert(false); }, 2000);
      setAlert(true);
    }

    event.target.checked = false;
  }


  const parseExplanation = () => {
    if (output.explanation && output.explanation.length > 0) {
      return (
        <ol>
          {
            output.explanation.map(node => {
              return (<li key={node}>{node}</li>);
            })}
        </ol >
      );
    }
    else {
      return ("");
    }
  }

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
      "predicates": [],
      "selectivity": 50,
    });
    setOutput({
      "plans": 0,
      "output": "",
      "explanation": [],
    });
  }

  const showSelectedPredicates = () => {
    if (input.predicates && input.predicates.length > 0) {
      let output = "";
      input.predicates.forEach((predicate) => {
        output += `${predicate}, `
      })
      return (output.slice(0, output.length-2));
    }
    else {
      return "";
    }
  }

  return (
    <>
      {
        showAlert ? <Card className="position-fixed" style={{ zIndex: 100, backgroundColor: "red", color: "white", top: 50 + '%', left: 50 + '%', transform: `translate(-50%, -50%)`}}>
        <Card.Body>You may only select a maximum of 4 predicates.</Card.Body>
      </Card> : null
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

      <FormOutput parseExplanation={parseExplanation} output={output}/>
    </>
  )
}
      
export default FormInput;