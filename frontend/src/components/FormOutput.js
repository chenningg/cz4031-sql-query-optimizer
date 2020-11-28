import Form from 'react-bootstrap/Form'
import Col from 'react-bootstrap/Col'

const FormOutput = (props) => {
  const renderAlternativeSelector = () => {
    if (props.output.plans <= 0) {
      return <option>No alternatives available.</option>;
    }
    else if (props.output.plans === 1) {
      return (<option>1</option>);
    }
    else {
      let planOptions = [];
      for (let i = 0; i < props.output.plans; i++) {
        planOptions.push(
          <option>{i}</option>
        )
      }
      return (planOptions);
    }
  }

  return (
    <>
      <Form.Row>
        <Form.Group as={Col} controlId="formOutputHeader">
          <h1>Output</h1>
        </Form.Group>
        <Form.Group as={Col} controlId="formAlternativeSelector">
          <Form.Label><b>Select alternative plan:</b></Form.Label>
          <Form.Control as="select">
            {renderAlternativeSelector()}
          </Form.Control>
        </Form.Group>
      </Form.Row>
      <Form.Row>
        <Form.Group as={Col} controlId="formOutput">
          <Form.Label>Optimal plan</Form.Label>
          <Form.Control as="textarea" rows="20" value={JSON.stringify(props.output.output, null, 2)} readOnly />
        </Form.Group>
        <Form.Group as={Col} controlId="formAlternative">
          <Form.Label>Alternative plan</Form.Label>
          <Form.Control as="textarea" rows="20" value={props.parseExplanation()} readOnly />
        </Form.Group>
      </Form.Row>

      <Form.Row>
        <Form.Group as={Col} controlId="formOutputExplanation">
          <Form.Label>Optimal explanation</Form.Label>
          <Form.Control as="textarea" rows="20" value={props.parseExplanation()} readOnly />
        </Form.Group>
        <Form.Group as={Col} controlId="formAlternativeExplanation">
          <Form.Label>Alternative Explanation</Form.Label>
          <Form.Control as="textarea" rows="20" value={props.parseExplanation()} readOnly />
        </Form.Group>
      </Form.Row>
    </>
  )
}

export default FormOutput;