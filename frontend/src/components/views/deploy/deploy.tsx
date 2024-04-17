import * as React from "react";
import { Tabs } from "antd";
import { ArrowTopRightOnSquareIcon, ChatBubbleOvalLeftEllipsisIcon, GlobeAltIcon, RocketLaunchIcon } from "@heroicons/react/24/outline";

const DeployView = () => {
  return (
    <div className=" ">
      <div className="mb-4 text-primary">
        {" "}
        <Tabs
          tabBarStyle={{ paddingLeft: 0, marginLeft: 0 }}
          defaultActiveKey="1"
          tabPosition="left"
          items={[
            {
              label: (
                <div className="w-full  ">
                  {" "}
                  <ChatBubbleOvalLeftEllipsisIcon className="h-4 w-4 inline-block mr-1" />
                  WhatsApp
                </div>
              ),
              key: "1",
              children: <div className="text-center p-4">Integrate with WhatsApp easily. Coming soon! <RocketLaunchIcon className="h-5 w-5 inline-block" /></div>,
            },
            {
              label: (
                <>
                  <GlobeAltIcon className="h-4 w-4 inline-block mr-1" />
                  Website Widget
                </>
              ),
              key: "2",
              children: <div className="text-center p-4">Embed directly into your website. Coming soon! <RocketLaunchIcon className="h-5 w-5 inline-block" /></div>,
            },
            {
              label: (
                <>
                  <ArrowTopRightOnSquareIcon className="h-4 w-4 inline-block mr-1" />
                  API Integration
                </>
              ),
              key: "3",
              children: <div className="text-center p-4">Connect through our robust API. Coming soon! <RocketLaunchIcon className="h-5 w-5 inline-block" /></div>,
            },
            {
              label: (
                <>
                  <RocketLaunchIcon className="h-4 w-4 inline-block mr-1" />
                  Custom Deployment
                </>
              ),
              key: "4",
              children: <div className="text-center p-4">Deploy on your own infrastructure. Contact us for more information.</div>,
            },
          ]}
        />
      </div>

      <div></div>
    </div>
  );
};

export default DeployView;
