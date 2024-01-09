import * as React from "react";
import Icon from "./icons";

const Footer = () => {
  return (
    <div className=" mt-4 text-primary p-3  border-t border-secondary ">
      <div className="text-xs">
        <span className="text-accent hidden inline-block mr-1  ">
          {" "}
          <Icon icon="app" size={8} />
        </span>
      </div>
    </div>
  );
};
export default Footer;
