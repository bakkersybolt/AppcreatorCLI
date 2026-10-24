// `app.json` is written by appcreator when the project is generated (JSON, so any app name stays prettier-proof).
import app from './app.json'

/** Name of the app, shown in the header and on the start page. */
export const APP_NAME: string = app.name

/** The AI assistants the project was generated for (shown on the start page). */
export const ASSISTANT_NAMES: string = app.assistants
