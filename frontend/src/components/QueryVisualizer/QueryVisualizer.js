import DagreGraph from 'dagre-d3-react'

import styles from "./QueryVisualizer.module.css"

const QueryVisualizer = (props) => {

  const nodes = [];
  const links = [];

  const getData = () => {
    console.log(props);
    if (props.data && "nodes" in props.data && "links" in props.data) {
      props.data["nodes"].forEach((node) => {
        nodes.push({ id: node.id, label: node.node_type, class: `${styles.queryNode}`});
      })

      props.data["links"].forEach((link) => {
        links.push({ source: link.source, target: link.target, class: `${styles.queryLink}` });
      })
    }
    else {
      return null;
    }
  }

  const onNodeClick = (event) => {
    console.log(event);
  }

  return (
    getData() !== null ?
    <>  
      <DagreGraph
        nodes={nodes}
        links={links}
        config={{
          rankdir: 'TB',
          align: 'UL',
          ranker: 'tight-tree'
        }}
        width='100%'
        height='100%'
        animate={1000}
        shape='rect'
        fitBoundaries={true}
        zoomable>
      </DagreGraph >
    </> : "Waiting for data..."
  )
}

export default QueryVisualizer;