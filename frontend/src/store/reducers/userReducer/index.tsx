import * as usersActions from "../../actions/usersActions/constants";

const initialState = {
  loggedIn: false,
  accessToken: null,
  user: {},
  email: ""
};

export default (state = initialState, action: any) => {
  switch (action.type) {
    case usersActions.SIGN_IN:
    case usersActions.SIGN_UP:
      return {
        ...state,
        loggedIn: true,
        accessToken: action.payload.token,
        user: action.payload?.user ?? {},
      };
    case usersActions.SET_EMAIL:
      return {
        ...state,
        email: action.payload
      };
    case usersActions.RESET_STATE:
      return initialState;
    default:
      return state;
  }
};
