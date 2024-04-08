import {
  InformationCircleIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { Modal, message } from "antd";
import * as React from "react";
import { IAgentFlowSpec, IStatus } from "../../types";
import { useSelector } from "react-redux";
import { fetchJSON, getServerUrl, sampleWorkflowConfig, timeAgo, truncateText } from "../../utils";
import {
  AgentFlowSpecView,
  BounceLoader,
  Card,
  LaunchButton,
  LoadBox,
  LoadingOverlay,
} from "../../atoms";

const AgentsView = ({}: any) => {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<IStatus | null>({
    status: true,
    message: "All good",
  });

  const loggedIn = useSelector(state => state.user.loggedIn);
  const serverUrl = getServerUrl();
  const listAgentsUrl = `${serverUrl}/agent/list`;
  const saveAgentsUrl = `${serverUrl}/agent`;
  const deleteAgentUrl = `${serverUrl}/agent`;

  const [agents, setAgents] = React.useState<IAgentFlowSpec[] | null>([]);
  const [selectedAgent, setSelectedAgent] =
    React.useState<IAgentFlowSpec | null>(null);

  const [showNewAgentModal, setShowNewAgentModal] = React.useState(false);

  const [showAgentModal, setShowAgentModal] = React.useState(false);

  const sampleAgent: IAgentFlowSpec = {
    type: "assistant",
    description: "Sample assistant",
    // reuse the value defined in sampleWorkflowConfig.receiver.config.system_message
    config: {
      name: "sample_assistant",
      system_message: sampleWorkflowConfig.receiver.config.system_message,
    },
  };
  const [newAgent, setNewAgent] = React.useState<IAgentFlowSpec | null>(
    sampleAgent
  );

  const deleteAgent = (agent: IAgentFlowSpec) => {
    setError(null);
    setLoading(true);
    // const fetch;
    const payLoad = {
      method: "DELETE",
      headers: {},
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);
        fetchAgents();
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(`${deleteAgentUrl}?id=${agent.id}`, payLoad, onSuccess, onError);
  };

  const fetchAgents = () => {
    setError(null);
    setLoading(true);
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        // message.success(data.message);
        // console.log("agents", data.data);
        setAgents(data.data);
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(listAgentsUrl, payLoad, onSuccess, onError);
  };

  const saveAgent = (agent: IAgentFlowSpec) => {
    setError(null);
    setLoading(true);
    // const fetch;

    const payLoad = {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(agent),
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);
        fetchAgents();
      } else {
        message.error(data.message);
      }
      setLoading(false);
      setNewAgent(sampleAgent);
    };
    const onError = (err: any) => {
      setError(err);
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(saveAgentsUrl, payLoad, onSuccess, onError);
  };

  React.useEffect(() => {
    if (loggedIn) {
      fetchAgents();
    }
  }, []);

  const agentRows = (agents || []).map((agent: IAgentFlowSpec, i: number) => {
    return (
      <div key={"agentrow" + i} className=" " style={{ width: "200px" }}>
        <div className="">
          <Card
            className="h-full p-2 cursor-pointer"
            title={
              <div className="  ">{truncateText(agent.config.name, 25)}</div>
            }
            onClick={() => {
              setSelectedAgent(agent);
              setShowAgentModal(true);
            }}
          >
            <div style={{ minHeight: "65px" }} className="my-2   break-words">
              {" "}
              {truncateText(agent.description || "", 70)}
            </div>
            <div className="text-xs">{timeAgo(agent.timestamp || "")}</div>
            <div
              onMouseEnter={(e) => {
                e.stopPropagation();
              }}
              className=" mt-2 text-right opacity-0 group-hover:opacity-100 "
            >
              {" "}
              <div
                role="button"
                className="text-accent text-xs inline-block hover:bg-primary p-2 rounded"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteAgent(agent);
                }}
              >
                <TrashIcon className=" w-5, h-5 cursor-pointer inline-block" />
                <span className="text-xs hidden"> delete</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  });

  const AgentModal = ({
    agent,
    setAgent,
    showAgentModal,
    setShowAgentModal,
    handler,
  }: {
    agent: IAgentFlowSpec | null;
    setAgent: (agent: IAgentFlowSpec | null) => void;
    showAgentModal: boolean;
    setShowAgentModal: (show: boolean) => void;
    handler?: (agent: IAgentFlowSpec | null) => void;
  }) => {
    const [localAgent, setLocalAgent] = React.useState<IAgentFlowSpec | null>(
      agent
    );

    return (
      <Modal
        title={
          <>
            Agent Specification{" "}
            <span className="text-accent font-normal">
              {agent?.config.name}
            </span>{" "}
          </>
        }
        width={800}
        open={showAgentModal}
        onOk={() => {
          setAgent(null);
          setShowAgentModal(false);
          if (handler) {
            handler(localAgent);
          }
        }}
        onCancel={() => {
          setAgent(null);
          setShowAgentModal(false);
        }}
      >
        {agent && (
          <AgentFlowSpecView
            title=""
            flowSpec={localAgent || agent}
            setFlowSpec={setLocalAgent}
          />
        )}
        {/* {JSON.stringify(localAgent)} */}
      </Modal>
    );
  };

  return (
    <div className="text-primary  ">
      <AgentModal
        agent={selectedAgent}
        setAgent={setSelectedAgent}
        setShowAgentModal={setShowAgentModal}
        showAgentModal={showAgentModal}
        handler={(agent: IAgentFlowSpec | null) => {
          if (agent) {
            saveAgent(agent);
          }
        }}
      />

      <AgentModal
        agent={newAgent || sampleAgent}
        setAgent={setNewAgent}
        setShowAgentModal={setShowNewAgentModal}
        showAgentModal={showNewAgentModal}
        handler={(agent: IAgentFlowSpec | null) => {
          if (agent) {
            saveAgent(agent);
          }
        }}
      />

      <div className="mb-2   relative">
        <div className="     rounded  ">
          <div className="flex mt-2 pb-2 mb-2 border-b">
            <div className="flex-1 font-semibold mb-2 ">
              {" "}
              Agents ({agentRows.length}){" "}
            </div>
            <LaunchButton
              className="text-sm p-2 px-3"
              onClick={() => {
                setShowNewAgentModal(true);
              }}
            >
              {" "}
              <PlusIcon className="w-5 h-5 inline-block mr-1" />
              New Agent
            </LaunchButton>
          </div>

          <div className="text-xs mb-2 pb-1  ">
            {" "}
            Configure an agent that can reused in your agent workflow{" "}
            {selectedAgent?.config.name}
          </div>
          {agents && agents.length > 0 && (
            <div className="w-full  relative">
              <LoadingOverlay loading={loading} />
              <div className="   flex flex-wrap gap-3">{agentRows}</div>
            </div>
          )}

          {agents && agents.length === 0 && !loading && (
            <div className="text-sm border mt-4 rounded text-secondary p-2">
              <InformationCircleIcon className="h-4 w-4 inline mr-1" />
              No agents found. Please create a new agent.
            </div>
          )}

          {loading && (
            <div className="  w-full text-center">
              {" "}
              <BounceLoader />{" "}
              <span className="inline-block"> loading .. </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentsView;
