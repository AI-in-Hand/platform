import React from "react";
import {graphql} from "gatsby"
import Layout from "../../components/layout";
import LogInVerify from "../../components/register";

const RegisterForm = ({ data }: any) => {
    return (
        <Layout meta={data.site.siteMetadata} title="Sign-Up" link={'sing-up'}>
            <LogInVerify/>
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

export default RegisterForm;
