import * as React from "react";
import SkillsView from "./skills";
import AgentsView from "./agents";
import WorkflowView from "./workflow";
import { Tabs } from "antd";
import {
  VariableIcon,
  UserIcon,
  UserGroupIcon,
  WrenchIcon,
} from "@heroicons/react/24/outline";
import UserVariables from '../../userVariables';

const BuildView = () => {
  return (
    <div className=" ">
      <div className="mb-6 text-sm text-primary">
        <details>
          <summary className="text-primary mb-2">Getting Started</summary>
          <div>
            <p className="mb-4">
              Welcome to the <strong>Build</strong> section! This is where you set up and manage the components that make your AI solutions work.
            </p>
            <p className="mb-4">
              <strong>Variables</strong> are used to store API keys, credentials, or any other data your skills need. They keep sensitive information safe while still letting your skills access it.
            </p>
            <p className="mb-4">
              <strong>Skills</strong> are what give your agents their special abilities. They let your agents make API calls, perform calculations, and do other tasks.
            </p>
            <p className="mb-4">
              <strong>Agents</strong> are like your digital workers. You give each one instructions and skills to do specific tasks.
            </p>
            <p>
              <strong>Teams</strong> are how you organize your agents to automate workflows. You can define communication flows to coordinate the work of multiple agents.
            </p>
          </div>
        </details>
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
                <>
                  <VariableIcon className="h-4 w-4 inline-block mr-1" />
                  Variables
                </>
              ),
              key: "1",
              children: <UserVariables />,
            },
            {
              label: (
                <div className="w-full  ">
                  {" "}
                  <WrenchIcon className="h-4 w-4 inline-block mr-1" />
                  Skills
                </div>
              ),
              key: "2",
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
                  Teams
                </>
              ),
              key: "4",
              children: <WorkflowView />,
            },
          ]}
        />
      </div>

      <div></div>
    </div>
  );
};

export default BuildView;
