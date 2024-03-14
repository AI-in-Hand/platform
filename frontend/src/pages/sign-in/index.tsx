import React from "react";
import {graphql} from "gatsby"
import Layout from "../../components/layout";
import Login from "../../components/login";

const LoginForm = ({ data }: any) => {
  return (
      <Layout meta={data.site.siteMetadata} title="Sign-In" link={'sing-in'}>
        <Login/>
      </Layout>
  );
};

export const query = graphql`
  query HomePageQuery {
    site {
      siteMetadata {
        description
        title
      }
    }
  }
`;

export default LoginForm;
