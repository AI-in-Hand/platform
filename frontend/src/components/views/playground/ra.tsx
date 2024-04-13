import * as React from "react";
import { IChatSession, IMessage, IStatus } from "../../types";
import { fetchJSON, getServerUrl } from "../../api_utils";
import { setLocalStorage } from "../../utils";
import ChatBox from "./chatbox";
import { useSelector } from "react-redux";
import { message } from "antd";
import SideBarView from "./sidebar";
import { useConfigStore } from "../../../hooks/store";
import SessionsView from "./sessions";

const RAView = () => {
  const session: IChatSession | null = useConfigStore((state) => state.session);
  const [loading, setLoading] = React.useState(false);
  const [messages, setMessages] = React.useState<IMessage[] | null>(null);
  const [skillUpdated, setSkillUpdated] = React.useState("default");

  const skillup = {
    get: skillUpdated,
    set: setSkillUpdated,
  };

  const [config, setConfig] = React.useState(null);

  React.useEffect(() => {
    setLocalStorage("ara_config", config);
  }, [config]);

  const [error, setError] = React.useState<IStatus | null>({
    status: true,
    message: "All good",
  });

  const loggedIn = useSelector(state => state.user.loggedIn);
  const serverUrl = getServerUrl();
  const workflowConfig = useConfigStore((state) => state.workflowConfig);

  const fetchMessages = (session: IChatSession | null, after: string | null = null) => {
    setError(null);
    setLoading(true);
    setMessages(null);

    const fetchMessagesUrl = `${serverUrl}/message/list?session_id=${session?.id}${after ? `&after=${after}` : ""}`;
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        setMessages(data.data);
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

    fetchJSON(fetchMessagesUrl, payLoad, onSuccess, onError);
  };

  React.useEffect(() => {
    if (loggedIn && session) {
      fetchMessages(session)
        .then((data) => {
          setMessages(data);
        })
        .catch((error) => {
          console.error("Error fetching messages:", error);
          message.error(error.message);
        });
    }
  }, [loggedIn, session]);

  return (
    <div className="h-full">
      <div className="flex h-full">
        <div className="mr-2 rounded">
          <SideBarView />
        </div>
        <div className="flex-1">
          {!session && (
            <div className="w-full h-full flex items-center justify-center">
              <div className="w-2/3" id="middle">
                <div className="w-full text-center">
                  <img
                    src="/images/svgs/welcome.svg"
                    alt="welcome"
                    className="text-accent inline-block object-cover w-56"
                  />
                </div>
                <SessionsView />
              </div>
            </div>
          )}
          {workflowConfig !== null && session !== null && (
            <ChatBox initMessages={messages} />
          )}
        </div>
      </div>
    </div>
  );
};

export default RAView;
