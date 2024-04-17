import * as React from "react";
import { Tabs } from "antd";
import { ArrowTopRightOnSquareIcon, ChatBubbleOvalLeftEllipsisIcon, PuzzleIcon, RocketLaunchIcon } from "@heroicons/react/24/outline";


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
              <div className="w-full flex justify-center items-center">
                <ChatBubbleOvalLeftEllipsisIcon />
                WhatsApp
              </div>
            ),
            key: "2",
            children: <div className="text-center p-4">Integrate with WhatsApp easily. Coming soon! <RocketLaunchIcon className="h-5 w-5 inline-block" /></div>,
          },
          {
            label: (
              <div className="w-full flex justify-center items-center">
                <PuzzleIcon className="h-5 w-5 mr-2" />
                Website Widget
              </div>
            ),
            key: "3",
            children: <div className="text-center p-4">Embed directly into your website. Coming soon! <RocketLaunchIcon className="h-5 w-5 inline-block" /></div>,
          },
          {
            label: (
              <div className="w-full flex justify-center items-center">
                <ArrowTopRightOnSquareIcon />
                API Integration
              </div>
            ),
            key: "4",
            children: <div className="text-center p-4">Connect through our robust API. Coming soon! <RocketLaunchIcon className="h-5 w-5 inline-block" /></div>,
          },
          {
            label: (
              <div className="w-full flex justify-center items-center">
                <RocketLaunchIcon className="h-5 w-5 mr-2" />
                Custom Deployment
              </div>
            ),
            key: "5",
            children: <div className="text-center p-4">Deploy on your own infrastructure. Contact us for more information.</div>,
          },
        ]}
      />
    </div>
  );
};

export default DeployView;
