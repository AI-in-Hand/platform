import * as React from "react";
import { Tabs } from "antd";
import {
  RocketIcon,
} from "@heroicons/react/24/outline";

const DeployView = () => {
  return (
    <div>
      <Tabs
        tabBarStyle={{ paddingLeft: 0, marginLeft: 0 }}
        defaultActiveKey="1"
        tabPosition="left"
        items={[
          {
            label: (
              <div className="w-full">
                <RocketIcon className="h-4 w-4 inline-block mr-1" />
                Deploy
              </div>
            ),
            key: "1",
            children: <div className="text-center p-4">Coming soon!</div>,
          },
        ]}
      />
    </div>
  );
};

export default DeployView;
