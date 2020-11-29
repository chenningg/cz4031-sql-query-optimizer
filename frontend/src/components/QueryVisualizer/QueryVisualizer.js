import {useState, useEffect} from "react"
import DagreGraph from 'dagre-d3-react'

import styles from "./QueryVisualizer.module.css"

const QueryVisualizer = (props) => {

  const nodes = [];
  const links = [];

  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipText, setTooltipText] = useState("");

  useEffect(() => {
    setShowTooltip(false);
  }, [props.output])

  const getData = () => {
    if (props.output["error"] === false && props.output["data"].hasOwnProperty(props.planId)) {
      console.log(props.output);
      props.output.data[props.planId]["graph"]["nodes"].forEach((node) => {
        nodes.push({ id: node.id, label: `${node.node_type}\nCost: ${node.cost.toFixed(2)}`, class: `${styles.queryNode}`});
      })

      props.output.data[props.planId]["graph"]["links"].forEach((link) => {
        links.push({ source: link.source, target: link.target, class: `${styles.queryLink}` });
      })
    }
    else {
      return null;
    }
  }

  const onNodeClick = (event) => {
    if ("original" in event) {
      const nodeId = event["original"]["id"];
      props.output.data[props.planId]["graph"]["nodes"].forEach((node) => {
        if (node["id"] === nodeId) {
          setTooltipText(JSON.stringify(node, null, 2));
          setShowTooltip(true);
          return;
        }
      })
    }
  }

  return (
    getData() !== null ?
    <div className={styles.graphWrapper}>
      <div className={`${styles.graphTooltip} ${showTooltip ? "" : styles.hideTooltip}`}>
          <span className={styles.tooltipText}>{tooltipText}</span>
          <button className={styles.hideTooltipButton} onClick={() => {setShowTooltip(false)}}>Hide</button>
      </div>  
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
        zoomable
        onNodeClick={onNodeClick}>
      </DagreGraph >
    </div> :
    <div className={styles.graphLoadingWrapper}>
      <p>Waiting for data...</p>
    </div>
  )
}

export default QueryVisualizer;