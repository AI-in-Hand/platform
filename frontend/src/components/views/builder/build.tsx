import * as React from "react";
import SkillsView from "./skills";
import AgentsView from "./agents";
import WorkflowView from "./workflow";
import { Tabs } from "antd";
import {
  KeyIcon,
  UserIcon,
  UserGroupIcon,
  WrenchIcon,
} from "@heroicons/react/24/outline";
import UserVariables from '../../userVariables';

const BuildView = () => {
  return (
    <div className=" ">
      {/* <div className="mb-4 text-2xl">Build </div> */}
      <div className="mb-6 text-sm hidden text-secondary">
        {" "}
        Create skills, agents and workflows for building multiagent capabilities{" "}
      </div>

      <div className="mb-4 text-primary">
        {" "}
        <Tabs
          tabBarStyle={{ paddingLeft: 0, marginLeft: 0 }}
          defaultActiveKey="4"
          tabPosition="left"
          items={[
            {
              label: (
                <div className="w-full  ">
                  {" "}
                  <WrenchIcon className="h-4 w-4 inline-block mr-1" />
                  Skills
                </div>
              ),
              key: "1",
              children: <SkillsView />,
            },
            {
              label: (
                <>
                  <UserIcon className="h-4 w-4 inline-block mr-1" />
                  Agents
                </>
              ),
              key: "3",
              children: <AgentsView />,
            },
            {
              label: (
                <>
                  <UserGroupIcon className="h-4 w-4 inline-block mr-1" />
                  Workflows
                </>
              ),
              key: "4",
              children: <WorkflowView />,
            },
            {
              label: (
                <>
                  <KeyIcon className="h-4 w-4 inline-block mr-1" />
                  API Keys
                </>
              ),
              key: "5",
              children: <UserVariables />,
            },
          ]}
        />
      </div>

      <div></div>
    </div>
  );
};

export default BuildView;
