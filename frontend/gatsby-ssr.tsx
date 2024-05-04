import React from "react";

const codeToRunOnClient = `(function() {
  try {
    var mode = localStorage.getItem('darkmode');
    document.getElementsByTagName("html")[0].className === 'dark' ? 'dark' : 'light';
  } catch (e) {}
})();`;

export const onRenderBody = ({ setHeadComponents, setPostBodyComponents }) => {
  setHeadComponents([
    <script
      key="darkmode-script"
      dangerouslySetInnerHTML={{ __html: codeToRunOnClient }}
    />,
  ]);

  setPostBodyComponents([
    <script key="chatbot-widget" src="/chatbot-widget.js" type="text/javascript" />,
  ]);
};
