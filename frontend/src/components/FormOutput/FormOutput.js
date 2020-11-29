import Form from 'react-bootstrap/Form'
import Col from 'react-bootstrap/Col'

import QueryVisualizer from "../QueryVisualizer/QueryVisualizer"

const FormOutput = (props) => {
  const renderAlternativeSelector = () => {
    return <option>No alternatives available.</option>;
  }

  const parseExplanation = () => {
    if (props.explanation && props.explanation.hasOwnProperty("nodes")) {
      return (
        <ol>
        </ol >
      );
    }
    else {
      return ("test");
    }
  }

  return (
    <>
      <Form.Row>
        <h1>Compare plans</h1>
      </Form.Row>
      <Form.Row>
        <Form.Group as={Col} controlId="formAlternativeSelector">
          <Form.Label><b>Select plan:</b></Form.Label>
          <Form.Control as="select">
            {renderAlternativeSelector()}
          </Form.Control>
        </Form.Group>
        <Form.Group as={Col} controlId="formAlternativeSelector">
          <Form.Label><b>Select plan:</b></Form.Label>
          <Form.Control as="select">
            {renderAlternativeSelector()}
          </Form.Control>
        </Form.Group>
      </Form.Row>
      <Form.Row>
        <Form.Group as={Col} controlId="formGraph1">
          <QueryVisualizer data={props.explanation}/>
        </Form.Group>
        <Form.Group as={Col} controlId="formGraph2">
          <QueryVisualizer data={props.explanation}/>
        </Form.Group>
      </Form.Row>
      
      <Form.Row>
        <Form.Group as={Col} controlId="formOutput">
          <Form.Label>Optimal plan</Form.Label>
          <Form.Control as="textarea" rows="20" value={JSON.stringify(props.output, null, 2)} readOnly />
        </Form.Group>
        <Form.Group as={Col} controlId="formAlternative">
          <Form.Label>Alternative plan</Form.Label>
          <Form.Control as="textarea" rows="20" value={parseExplanation()} readOnly />
        </Form.Group>
      </Form.Row>
    </>
  )
}

export default FormOutput;