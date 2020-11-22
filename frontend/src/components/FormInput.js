import { useState } from 'react';
import axios from "axios";

import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Col from 'react-bootstrap/Col'
import Accordion from 'react-bootstrap/Accordion'
import Card from 'react-bootstrap/Card'

const FormInput = () => {
  const [query, setQuery] = useState("");
  const [output, setOutput] = useState("");

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
    <>
      <Form onSubmit={handleSubmit} className="mb-4">
        <Form.Row>
          <Form.Group as={Col} controlId="formOptions">
            <Form.Group controlId="formSelectivity">
              <Form.Label>Selectivity</Form.Label>
              <Form.Control type="range" custom />
            </Form.Group>

            <Form.Group controlId="formPredicates">
              <Form.Label>Predicates</Form.Label>
              <Accordion>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="0">
                    Region
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="0">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="r_regionkey" label="r_regionkey" />
                      <Form.Check
                      type="checkbox"
                        id="r_name" label="r_name" />
                      <Form.Check
                      type="checkbox"
                        id="r_comment" label="r_comment"/>
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="1">
                    Nation
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="1">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="n_nationkey" label="n_nationkey" />
                      <Form.Check
                      type="checkbox"
                        id="n_name" label="n_name" />
                      <Form.Check
                      type="checkbox"
                        id="n_regionkey" label="n_regionkey" />
                      <Form.Check
                      type="checkbox"
                        id="n_comment" label="n_comment"/>
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="2">
                    Supplier
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="2">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="s_suppkey" label="s_suppkey" />
                      <Form.Check
                      type="checkbox"
                        id="s_name" label="s_name" />
                      <Form.Check
                      type="checkbox"
                        id="s_address" label="s_address" />
                      <Form.Check
                      type="checkbox"
                        id="s_nationkey" label="s_nationkey" />
                      <Form.Check
                      type="checkbox"
                        id="s_phone" label="s_phone" />
                      <Form.Check
                      type="checkbox"
                        id="s_acctbal" label="s_acctbal" />
                      <Form.Check
                      type="checkbox"
                        id="s_comment" label="s_comment" />
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="3">
                    Customer
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="3">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="c_custkey" label="c_custkey" />
                      <Form.Check
                      type="checkbox"
                        id="c_name" label="c_name" />
                      <Form.Check
                      type="checkbox"
                        id="c_address" label="c_address" />
                      <Form.Check
                      type="checkbox"
                        id="c_nationkey" label="c_nationkey" />
                      <Form.Check
                      type="checkbox"
                        id="c_phone" label="c_phone" />
                      <Form.Check
                      type="checkbox"
                        id="c_acctbal" label="c_acctbal" />
                      <Form.Check
                      type="checkbox"
                        id="c_mktsegment" label="c_mktsegment" />
                      <Form.Check
                      type="checkbox"
                        id="c_comment" label="c_comment" />
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="4">
                    Part
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="4">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="p_partkey" label="p_partkey" />
                      <Form.Check
                      type="checkbox"
                        id="p_name" label="p_name" />
                      <Form.Check
                      type="checkbox"
                        id="p_mfgr" label="p_mfgr" />
                      <Form.Check
                      type="checkbox"
                        id="p_brand" label="p_brand" />
                      <Form.Check
                      type="checkbox"
                        id="p_type" label="p_type" />
                      <Form.Check
                      type="checkbox"
                        id="p_size" label="p_size" />
                      <Form.Check
                      type="checkbox"
                        id="p_container" label="p_container" />
                      <Form.Check
                      type="checkbox"
                        id="p_retailprice" label="p_retailprice" />
                      <Form.Check
                      type="checkbox"
                        id="p_comment" label="p_comment" />
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="5">
                    PartSupp
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="5">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="ps_partkey" label="ps_partkey" />
                      <Form.Check
                      type="checkbox"
                        id="ps_suppkey" label="ps_suppkey" />
                      <Form.Check
                      type="checkbox"
                        id="ps_availqty" label="ps_availqty" />
                      <Form.Check
                      type="checkbox"
                        id="ps_supplycost" label="ps_supplycost" />
                      <Form.Check
                      type="checkbox"
                        id="ps_comment" label="ps_comment" />
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="6">
                    Orders
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="6">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="o_orderkey" label="o_orderkey" />
                      <Form.Check
                      type="checkbox"
                        id="o_custkey" label="o_custkey" />
                      <Form.Check
                      type="checkbox"
                        id="o_orderstatus" label="o_orderstatus" />
                      <Form.Check
                      type="checkbox"
                        id="o_totalprice" label="o_totalprice" />
                      <Form.Check
                      type="checkbox"
                        id="o_orderdate" label="o_orderdate" />
                      <Form.Check
                      type="checkbox"
                        id="o_orderpriority" label="o_orderpriority" />
                      <Form.Check
                      type="checkbox"
                        id="o_clerk" label="o_clerk" />
                      <Form.Check
                      type="checkbox"
                        id="o_shippriority" label="o_shippriority" />
                      <Form.Check
                      type="checkbox"
                        id="o_comment" label="o_comment" />
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
                <Card>
                  <Accordion.Toggle as={Card.Header} variant="link" eventKey="7">
                    LineItem
                  </Accordion.Toggle>
                  <Accordion.Collapse eventKey="7">
                    <Card.Body>
                      <Form.Check
                      type="checkbox"
                        id="l_orderkey" label="l_orderkey" />
                      <Form.Check
                      type="checkbox"
                        id="l_partkey" label="l_partkey" />
                      <Form.Check
                      type="checkbox"
                        id="l_suppkey" label="l_suppkey" />
                      <Form.Check
                      type="checkbox"
                        id="l_linenumber" label="l_linenumber" />
                      <Form.Check
                      type="checkbox"
                        id="l_quantity" label="l_quantity" />
                      <Form.Check
                      type="checkbox"
                        id="l_extendedprice" label="l_extendedprice" />
                      <Form.Check
                      type="checkbox"
                        id="l_discount" label="l_discount" />
                      <Form.Check
                      type="checkbox"
                        id="l_tax" label="l_tax" />
                      <Form.Check
                      type="checkbox"
                        id="l_returnflag" label="l_returnflag" />
                      <Form.Check
                      type="checkbox"
                        id="l_linestatus" label="l_linestatus" />
                      <Form.Check
                      type="checkbox"
                        id="l_shipdate" label="l_shipdate" />
                      <Form.Check
                      type="checkbox"
                        id="l_commitdate" label="l_commitdate" />
                      <Form.Check
                      type="checkbox"
                        id="l_receiptdate" label="l_receiptdate" />
                      <Form.Check
                      type="checkbox"
                        id="l_shipinstruct" label="l_shipinstruct" />
                      <Form.Check
                      type="checkbox"
                        id="l_shipmode" label="l_shipmode" />
                    </Card.Body>
                  </Accordion.Collapse>
                </Card>
              </Accordion>
            </Form.Group>
          </Form.Group>
            
          <Form.Group as={Col} controlId="formQuery">
            <Form.Label>SQL Query</Form.Label>
            <Form.Control as="textarea" rows="19" placeholder="Input SQL query..." onChange={event => setQuery(event.target.value)} value={query} />
          
            <Button variant="primary" type="submit" className="w-100 mt-3">
            Generate
            </Button>
          </Form.Group>
        </Form.Row>
      </Form>

      <Form.Row>
        <Form.Group as={Col} controlId="formOutput">
          <Form.Label>Output</Form.Label>
          <Form.Control as="textarea" rows="15" value={output} />
        </Form.Group>
        <Form.Group as={Col} controlId="formExplanation">
          <Form.Label>Explanation</Form.Label>
          <Form.Control as="textarea" rows="15" />
        </Form.Group>
      </Form.Row>
    </>
  )
}
      
export default FormInput;