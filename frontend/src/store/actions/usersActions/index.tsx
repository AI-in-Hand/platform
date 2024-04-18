import * as usersActions from "./constants";


export function SignIn(data: {token: string, expiresIn: number, email: string, uid: string}) {
  return {
    type: usersActions.SIGN_IN,
    payload: data,
  };
}
export function SignUp(data: {token: string, expiresIn: number, email: string, uid: string}) {
  return {
    type: usersActions.SIGN_UP,
    payload: data,
  };
}
export function SetEmail(email: string) {
  return {
    type: usersActions.SET_EMAIL,
    payload: email,
  };
}
export function ResetState() {
  return {
    type: usersActions.RESET_STATE,
  };
}
export function RefreshToken(data: {token: string, expiresIn: number}) {
  return {
    type: usersActions.REFRESH_TOKEN,
    payload: data,
  };
}
export function SetActiveTab(activeTab: string) {
  return {
    type: usersActions.SET_ACTIVE_TAB,
    payload: activeTab,
  };
}