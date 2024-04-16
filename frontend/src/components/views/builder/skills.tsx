import {
  InformationCircleIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { Button, Input, Modal, message } from "antd";
import * as React from "react";
import { ISkill, IStatus } from "../../types";
import { useSelector } from "react-redux";
import { fetchJSON, getServerUrl } from "../../api_utils";
import {
  getSampleSkill,
  timeAgo,
  truncateText,
} from "../../utils";
import {
  BounceLoader,
  Card,
  CodeBlock,
  LaunchButton,
  LoadingOverlay,
  MonacoEditor,
} from "../../atoms";
import TextArea from "antd/es/input/TextArea";

const SkillsView = ({}: any) => {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<IStatus | null>({
    status: true,
    message: "All good",
  });

  const loggedIn = useSelector(state => state.user.loggedIn);
  const serverUrl = getServerUrl();
  const listSkillsUrl = `${serverUrl}/skill/list`;
  const saveSkillsUrl = `${serverUrl}/skill`;
  const deleteSkillsUrl = `${serverUrl}/skill`;

  const [skills, setSkills] = React.useState<ISkill[] | null>([]);
  const [selectedSkill, setSelectedSkill] = React.useState<any>(null);

  const [showSkillModal, setShowSkillModal] = React.useState(false);
  const [showNewSkillModal, setShowNewSkillModal] = React.useState(false);

  const sampleSkill = getSampleSkill();
  const [newSkill, setNewSkill] = React.useState<ISkill | null>(sampleSkill);

  const deleteSkill = (skill: ISkill) => {
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
        setSkills(data.data);
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
    fetchJSON(`${deleteSkillsUrl}?id=${skill.id}`, payLoad, onSuccess, onError);
  };

  const fetchSkills = () => {
    setError(null);
    setLoading(true);
    // const fetch;
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        // message.success(data.message);
        // console.log("skills", data.data);
        setSkills(data.data);
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
    fetchJSON(listSkillsUrl, payLoad, onSuccess, onError);
  };

  const saveSkill = (skill: ISkill) => {
    setError(null);
    setLoading(true);
    // const fetch;
    const payLoad = {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(skill),
    };

    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);
        // console.log("skills", data.data);
        setSkills(data.data);
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
    // TODO: enable saving skills (currently disabled)
    // fetchJSON(saveSkillsUrl, payLoad, onSuccess, onError);
    message.info("Saving skills is disabled for now. Coming soon!");
    setLoading(false);  // remove this line when saving is enabled
  };

  React.useEffect(() => {
    if (loggedIn) {
      // console.log("fetching messages", messages);
      fetchSkills();
    }
  }, []);

  const skillRows = (skills || []).map((skill: ISkill, i: number) => {
    return (
      <div key={"skillrow" + i} className=" " style={{ width: "200px" }}>
        <div>
          {" "}
          <Card
            className="h-full p-2 cursor-pointer group"
            title={truncateText(skill.title + (!skill.user_id ? " (public)" : ""), 35)}
            onClick={() => {
              setSelectedSkill(skill);
              setShowSkillModal(true);
            }}
          >
            <div style={{ minHeight: "65px" }} className="my-2   break-words">
              {" "}
              {truncateText(skill.description, 70) || truncateText(skill.content, 70)}
            </div>
            <div className="text-xs">{timeAgo(skill.timestamp || "")}</div>
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
                  deleteSkill(skill);
                }}
              >
                <TrashIcon className=" w-5, h-5 cursor-pointer inline-block" />
                <span className="text-xs hidden"> delete</span>
              </div>
            </div>
          </Card>
          <div className="text-right mt-2"></div>
        </div>
      </div>
    );
  });

  const SkillModal = ({
    skill,
    setSkill,
    showSkillModal,
    setShowSkillModal,
    handler,
  }: {
    skill: ISkill | null;
    setSkill: any;
    showSkillModal: boolean;
    setShowSkillModal: any;
    handler: any;
  }) => {
    const editorRef = React.useRef<any | null>(null);
    const [localSkill, setLocalSkill] = React.useState<ISkill | null>(skill);
    return (
      <Modal
        title={
          <>
            Skill Specification{" "}
            <span className="text-accent font-normal">{localSkill?.title}</span>{" "}
          </>
        }
        width={800}
        open={showSkillModal}
        onCancel={() => {
          setShowSkillModal(false);
        }}
        footer={[
          <Button
            key="back"
            onClick={() => {
              setShowSkillModal(false);
            }}
          >
            Cancel
          </Button>,
          <Button
            key="submit"
            type="primary"
            loading={loading}
            onClick={() => {
              setShowSkillModal(false);
              if (editorRef.current) {
                const content = editorRef.current.getValue();
                const updatedSkill = { ...localSkill, content, description: "" };
                setSkill(updatedSkill);
                handler(updatedSkill);
              }
            }}
          >
            Save
          </Button>,
        ]}
      >
        {localSkill && (
          <div style={{ minHeight: "70vh" }}>
            <div className="mb-2">
              <Input
                placeholder="Skill Title"
                value={localSkill.title}
                onChange={(e) => {
                  const updatedSkill = { ...localSkill, title: e.target.value };
                  setLocalSkill(updatedSkill);
                }}
              />
            </div>

            {/* <div className="mb-2">
              <div className="inline-block  "> Skill Description </div>
              <TextArea
                placeholder="Skill Description"
                value={localSkill.description}
                onChange={(e) => {
                  const updatedSkill = {
                    ...localSkill,
                    description: e.target.value,
                  };
                  setLocalSkill(updatedSkill);
                }}
              />
            </div> */}

            <div style={{ height: "70vh" }} className="h-full  mt-2 rounded">
              <MonacoEditor
                value={localSkill?.content}
                language="python"
                editorRef={editorRef}
              />
            </div>
          </div>
        )}
      </Modal>
    );
  };

  return (
    <div className=" text-primary ">
      {/* <Modal
        title={
          <div>
            <PlusIcon className="w-5 h-5 inline-block mr-1" /> Create New Skill
          </div>
        }
        width={800}
        open={showNewSkillModal}
        onOk={() => {
          saveSkill();
          setShowNewSkillModal(false);
        }}
        onCancel={() => {
          setShowNewSkillModal(false);
        }}
      >
        <>
          <div className="mb-2">
            Provide code for a new skill or create from current conversation.
          </div>
          <Input
            className="mb-2"
            placeholder="Skill Title"
            onChange={(e) => {
              setNewSkillTitle(e.target.value);
            }}
          />
          <TextArea
            value={skillCode}
            onChange={(e) => {
              setSkillCode(e.target.value);
            }}
            rows={10}
          />
        </>
      </Modal> */}

      <SkillModal
        skill={selectedSkill}
        setSkill={setSelectedSkill}
        showSkillModal={showSkillModal}
        setShowSkillModal={setShowSkillModal}
        handler={(skill: ISkill) => {
          saveSkill(skill);
        }}
      />

      <SkillModal
        skill={newSkill}
        setSkill={setNewSkill}
        showSkillModal={showNewSkillModal}
        setShowSkillModal={setShowNewSkillModal}
        handler={(skill: ISkill) => {
          saveSkill(skill);
        }}
      />

      <div className="mb-2   relative">
        <div className="">
          <div className="flex mt-2 pb-2 mb-2 border-b">
            <div className="flex-1 font-semibold mb-2 ">
              {" "}
              Skills ({skillRows.length}){" "}
            </div>
            <LaunchButton
              className="text-sm p-2 px-3"
              onClick={() => {
                // setShowNewSkillModal(true);
                message.info("Coming soon! In the meanwhile, try using existing skills.");
              }}
            >
              {" "}
              <PlusIcon className="w-5 h-5 inline-block mr-1" />
              New Skill
            </LaunchButton>
          </div>
          <div className="text-xs mb-2 pb-1  ">
            {" "}
            Skills are python functions that agents can use to solve tasks.{" "}
          </div>
          {skills && skills.length > 0 && (
            <div
              // style={{ height: "400px" }}
              className="w-full  relative"
            >
              <LoadingOverlay loading={loading} />
              <div className="   flex flex-wrap gap-3">{skillRows}</div>
            </div>
          )}

          {skills && skills.length === 0 && !loading && (
            <div className="text-sm border mt-4 rounded text-secondary p-2">
              <InformationCircleIcon className="h-4 w-4 inline mr-1" />
              No skills found. Please create a new skill.
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

export default SkillsView;
