import * as React from "react";
import { Tabs } from "antd";
import { ArrowTopRightOnSquareIcon, ChatBubbleOvalLeftEllipsisIcon, GlobeAltIcon, RocketLaunchIcon } from "@heroicons/react/24/outline";

const WhatsAppIntegration = () => (
  <div className="mb-2   relative">
    <div className="     rounded  ">
      <div className="flex mt-2 pb-2 mb-2 border-b text-primary">
        <div className="flex-1 font-semibold  mb-2 ">
          WhatsApp Integration
        </div>
      </div>
      <div className="text-xs mb-2 pb-1 text-secondary">
        Integrate with WhatsApp easily.
      </div>
      {(
        <div className="text-sm border mt-4 rounded text-secondary p-2">
          <RocketLaunchIcon className="h-4 w-4 inline mr-1" />
          Coming soon!
        </div>
      )}
    </div>
  </div>
);

const WebsiteWidget = () => (
  <div className="mb-2   relative">
    <div className="     rounded  ">
      <div className="flex mt-2 pb-2 mb-2 border-b text-primary">
        <div className="flex-1 font-semibold  mb-2 ">
          Website Widget
        </div>
      </div>
      <div className="text-xs mb-2 pb-1 text-secondary">
        Embed directly into your website.
      </div>
      {(
        <div className="text-sm border mt-4 rounded text-secondary p-2">
          <RocketLaunchIcon className="h-4 w-4 inline mr-1" />
          Coming soon!
        </div>
      )}
    </div>
  </div>
);

const APIIntegration = () => (
  <div className="mb-2   relative">
    <div className="     rounded  ">
      <div className="flex mt-2 pb-2 mb-2 border-b text-primary">
        <div className="flex-1 font-semibold  mb-2 ">
          API Integration
        </div>
      </div>
      <div className="text-xs mb-2 pb-1 text-secondary">
        Connect through our robust API.
      </div>
      {(
        <div className="text-sm border mt-4 rounded text-secondary p-2">
          <RocketLaunchIcon className="h-4 w-4 inline mr-1" />
          Coming soon!
        </div>
      )}
    </div>
  </div>
);

const CustomDeployment = () => (
  <div className="mb-2   relative">
    <div className="     rounded  ">
      <div className="flex mt-2 pb-2 mb-2 border-b text-primary">
        <div className="flex-1 font-semibold  mb-2 ">
          Custom Deployment
        </div>
      </div>
      <div className="text-xs mb-2 pb-1 text-secondary">
        Deploy on your own infrastructure.
      </div>
      {(
        <div className="text-sm border mt-4 rounded text-secondary p-2">
          <RocketLaunchIcon className="h-4 w-4 inline mr-1" />
          <u><a href="mailto:hello@ainhand.com" className="text-primary">Contact us</a></u> to learn more.
        </div>
      )}
    </div>
  </div>
);

const DeployView = () => {
  return (
    <div>
      <div className="mb-4 text-primary">
        <Tabs
          tabBarStyle={{ paddingLeft: 0, marginLeft: 0 }}
          defaultActiveKey="1"
          tabPosition="left"
          size="large"
          items={[
            {
              label: (
                <div className="w-full">
                  <ChatBubbleOvalLeftEllipsisIcon className="h-4 w-4 inline-block mr-1" />
                  WhatsApp
                </div>
              ),
              key: "1",
              children: <WhatsAppIntegration />,
            },
            {
              label: (
                <>
                  <GlobeAltIcon className="h-4 w-4 inline-block mr-1" />
                  Website Widget
                </>
              ),
              key: "2",
              children: <WebsiteWidget />,
            },
            {
              label: (
                <>
                  <ArrowTopRightOnSquareIcon className="h-4 w-4 inline-block mr-1" />
                  API Integration
                </>
              ),
              key: "3",
              children: <APIIntegration />,
            },
            {
              label: (
                <>
                  <RocketLaunchIcon className="h-4 w-4 inline-block mr-1" />
                  Custom Deployment
                </>
              ),
              key: "4",
              children: <CustomDeployment />,
            },
          ]}
        />
      </div>
    </div>
  );
};

export default DeployView;
