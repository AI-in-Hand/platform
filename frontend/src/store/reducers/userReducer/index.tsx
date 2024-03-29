import * as usersActions from "../../actions/usersActions/constants";

const initialState = {
  loggedIn: false,
  accessToken: null,
  expiresIn: null,
  user: {},
  email: ""
};

export default (state = initialState, action: any) => {
  switch (action.type) {
    case usersActions.SIGN_IN:
    case usersActions.SIGN_UP:
    case usersActions.REFRESH_TOKEN:
      return {
        ...state,
        loggedIn: true,
        accessToken: action.payload.token,
        expiresIn: action.payload.expiresIn,
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
