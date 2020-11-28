import Form from 'react-bootstrap/Form'
import Col from 'react-bootstrap/Col'

const FormOutput = (props) => {
  return (
    <Form.Row>
      <Form.Group as={Col} controlId="formOutput">
        <Form.Label>Optimal plan</Form.Label>
        <Form.Control as="textarea" rows="20" value={JSON.stringify(props.output.output, null, 2)} readOnly />
      </Form.Group>
      <Form.Group as={Col} controlId="formExplanation">
        <Form.Label>Explanation</Form.Label>
        <Form.Control as="textarea" rows="20" value={props.parseExplanation()} readOnly />
      </Form.Group>
    </Form.Row>
  )
}

export default FormOutput;