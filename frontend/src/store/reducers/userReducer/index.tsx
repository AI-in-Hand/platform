import * as usersActions from "../../actions/usersActions/constants";

const initialState = {
  loggedIn: false,
  accessToken: null,
  expiresIn: null,
  email: null,
  uid: null,
};

export default (state = initialState, action: any) => {
  switch (action.type) {
    case usersActions.SIGN_IN:
    case usersActions.SIGN_UP:
      return {
        ...state,
        loggedIn: true,
        accessToken: action.payload.token,
        expiresIn: action.payload.expiresIn,
        email: action.payload.email,
        uid: action.payload.uid,
      };
    case usersActions.REFRESH_TOKEN:
      return {
        ...state,
        accessToken: action.payload.token,
        expiresIn: action.payload.expiresIn,
      };
    case usersActions.SET_EMAIL:
      return {
        ...state,
        email: action.payload
      };
    case usersActions.RESET_STATE:
      // Reset all state except email (for login form)
      return {
        ...initialState,
        email: state.email
      };
    default:
      return state;
  }
};
