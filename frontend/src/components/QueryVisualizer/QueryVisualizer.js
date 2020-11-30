import {useState, useEffect} from "react"
import DagreGraph from 'dagre-d3-react'

import styles from "./QueryVisualizer.module.css"

const QueryVisualizer = (props) => {

  const nodes = [];
  const links = [];

  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipText, setTooltipText] = useState("");

  // Hide tooltip when either data changes or plan changes.
  useEffect(() => {
    setShowTooltip(false);
  }, [props.output, props.planId])

  // Loads data for nodes and links into graph.
  const getData = () => {
    if (props.output["error"] === false && props.output["data"].hasOwnProperty(props.planId)) {
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

  // When clicking on a graph's node, show tooltip with extra node data.
  const onNodeClick = (event) => {
    if ("original" in event) {
      const nodeId = event["original"]["id"];
      props.output.data[props.planId]["graph"]["nodes"].forEach((node) => {
        if (node["id"] === nodeId) {
          let nodeData = { ...node };
          nodeData["cost"] = parseFloat(nodeData["cost"]).toFixed(2);
          setTooltipText(JSON.stringify(nodeData, null, 2));
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
      <span>No data to show</span>
    </div>
  )
}

export default QueryVisualizer;