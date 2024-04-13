import {
  IAgentConfig,
  IAgentFlowSpec,
  IFlowConfig,
  IModelConfig,
  ISkill,
  IStatus,
} from "./types";

export function setCookie(name: string, value: any, days: number) {
  let expires = "";
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

export function getCookie(name: string) {
  const nameEQ = name + "=";
  const ca = document.cookie.split(";");
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == " ") c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}
export function setLocalStorage(
  name: string,
  value: any,
  stringify: boolean = true
) {
  if (stringify) {
    localStorage.setItem(name, JSON.stringify(value));
  } else {
    localStorage.setItem(name, value);
  }
}

export function getLocalStorage(name: string, stringify: boolean = true): any {
  if (typeof window !== "undefined") {
    const value = localStorage.getItem(name);
    try {
      if (stringify) {
        return JSON.parse(value!);
      } else {
        return value;
      }
    } catch (e) {
      return null;
    }
  } else {
    return null;
  }
}

export const capitalize = (s: string) => {
  if (typeof s !== "string") return "";
  return s.charAt(0).toUpperCase() + s.slice(1);
};

export function eraseCookie(name: string) {
  document.cookie = name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
}

export function truncateText(text: string, length = 50) {
  if (text.length > length) {
    return text.substring(0, length) + " ...";
  }
  return text;
}

export const getCaretCoordinates = () => {
  let caretX, caretY;
  const selection = window.getSelection();
  if (selection && selection?.rangeCount !== 0) {
    const range = selection.getRangeAt(0).cloneRange();
    range.collapse(false);
    const rect = range.getClientRects()[0];
    if (rect) {
      caretX = rect.left;
      caretY = rect.top;
    }
  }
  return { caretX, caretY };
};

export const getPrefixSuffix = (container: any) => {
  let prefix = "";
  let suffix = "";
  if (window.getSelection) {
    const sel = window.getSelection();
    if (sel && sel.rangeCount > 0) {
      let range = sel.getRangeAt(0).cloneRange();
      range.collapse(true);
      range.setStart(container!, 0);
      prefix = range.toString();

      range = sel.getRangeAt(0).cloneRange();
      range.collapse(true);
      range.setEnd(container, container.childNodes.length);

      suffix = range.toString();
      console.log("prefix", prefix);
      console.log("suffix", suffix);
    }
  }
  return { prefix, suffix };
};

export const uid = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

export const setCaretToEnd = (element: HTMLElement) => {
  const range = document.createRange();
  const selection = window.getSelection();
  range.selectNodeContents(element);
  range.collapse(false);
  selection?.removeAllRanges();
  selection?.addRange(range);
  element.focus();
};

// return a color between a start and end color using a percentage
export const ColorTween = (
  startColor: string,
  endColor: string,
  percent: number
) => {
  // example startColor = "#ff0000" endColor = "#0000ff" percent = 0.5
  const start = {
    r: parseInt(startColor.substring(1, 3), 16),
    g: parseInt(startColor.substring(3, 5), 16),
    b: parseInt(startColor.substring(5, 7), 16),
  };
  const end = {
    r: parseInt(endColor.substring(1, 3), 16),
    g: parseInt(endColor.substring(3, 5), 16),
    b: parseInt(endColor.substring(5, 7), 16),
  };
  const r = Math.floor(start.r + (end.r - start.r) * percent);
  const g = Math.floor(start.g + (end.g - start.g) * percent);
  const b = Math.floor(start.b + (end.b - start.b) * percent);
  return `rgb(${r}, ${g}, ${b})`;
};

export const guid = () => {
  var w = () => {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  };
  return `${w()}${w()}-${w()}-${w()}-${w()}-${w()}${w()}${w()}`;
};

/**
 * Takes a string and returns the first n characters followed by asterisks.
 * @param {string} str - The string to obscure
 * @param {number} n - Number of characters to show before obscuring
 * @returns {string} The obscured string with first n characters in clear text
 */
export const obscureString = (str: string, n: number = 3) => {
  if (n < 0 || n > str.length) {
    console.log("n cannot be less than 0 or greater than the string length.");
    return str;
  }
  // First n characters in clear text
  var clearText = str.substring(0, n);
  // Remaining characters replaced with asterisks
  var obscured = clearText + "*".repeat(str.length - n);

  return obscured;
};

/**
 * Converts a number of seconds into a human-readable string representing the duration in days, hours, minutes, and seconds.
 * @param {number} seconds - The number of seconds to convert.
 * @returns {string} A well-formatted duration string.
 */
export const formatDuration = (seconds: number) => {
  const units = [
    { label: " day", seconds: 86400 },
    { label: " hr", seconds: 3600 },
    { label: " min", seconds: 60 },
    { label: " sec", seconds: 1 },
  ];

  let remainingSeconds = seconds;
  const parts = [];

  for (const { label, seconds: unitSeconds } of units) {
    const count = Math.floor(remainingSeconds / unitSeconds);
    if (count > 0) {
      parts.push(count + (count > 1 ? label + "s" : label));
      remainingSeconds -= count * unitSeconds;
    }
  }

  return parts.length > 0 ? parts.join(" ") : "0 sec";
};

export const assistantConfigSystemMessage = "You are a helpful AI assistant. Solve tasks using your coding and language skills. In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. 1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself. 2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill. When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user. If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user. If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible. ";

export const sampleWorkflowConfig = (type = "twoagents") => {
  const llm_model_config: IModelConfig[] = [
    {
      model: "gpt-4-turbo-preview",
    },
  ];

  const userProxyConfig: IAgentConfig = {
    name: "userproxy",
    system_message: "You are a helpful assistant skilled at coordinating a group of other assistants to solve a task. ",
    code_execution_config: {
      work_dir: null,
      use_docker: false,
    },
  };
  const userProxyFlowSpec: IAgentFlowSpec = {
    type: "userproxy",
    config: userProxyConfig,
  };

  const assistantConfig: IAgentConfig = {
    name: "primary_assistant",
    system_message:
      assistantConfigSystemMessage,
  };

  const assistantFlowSpec: IAgentFlowSpec = {
    type: "assistant",
    config: assistantConfig,
  };

  const workFlowConfig: IFlowConfig = {
    name: "Default Agent Workflow",
    description: "Default Agent Workflow",
    sender: null,
    receiver: null,
    type: "twoagents",
  };

  return workFlowConfig;
};

export const getModels = () => {
  const models = [
    {
      model: "gpt-4-turbo-preview",
    },
    {
      model: "gpt-3.5-turbo",
    },
  ];
  return models;
};

export const getSampleSkill = () => {
  const content = `
  ## This is a sample skill. Replace with your own skill function
  ## In general, a good skill must have 3 sections:
  ## 1. Imports (import libraries needed for your skill)
  ## 2. Function definition  AND docstrings (this helps the LLM understand what the function does and how to use it)
  ## 3. Function body (the actual code that implements the function)

  import numpy as np
  import matplotlib.pyplot as plt
  from matplotlib import font_manager as fm

  def save_cat_ascii_art_to_png(filename='ascii_cat.png'):
      """
      Creates ASCII art of a cat and saves it to a PNG file.

      :param filename: str, the name of the PNG file to save the ASCII art.
      """
      # ASCII art string
      cat_art = [
          "  /\_/\  ",
          " ( o.o ) ",
          " > ^ <  "
      ]

      # Determine shape of output array
      height = len(cat_art)
      width = max(len(line) for line in cat_art)

      # Create a figure and axis to display ASCII art
      fig, ax = plt.subplots(figsize=(width, height))
      ax.axis('off')  # Hide axes

      # Get a monospace font
      prop = fm.FontProperties(family='monospace')

      # Display ASCII art using text
      for y, line in enumerate(cat_art):
          ax.text(0, height-y-1, line, fontproperties=prop, fontsize=12)

      # Adjust layout
      plt.tight_layout()

      # Save figure to file
      plt.savefig(filename, dpi=120, bbox_inches='tight', pad_inches=0.1)
      plt.close(fig)`;

  const skill: ISkill = {
    title: "save_cat_ascii_art_to_png",
    description: "save cat ascii art to png",
    content: content,
  };

  return skill;
};

export const timeAgo = (dateString: string): string => {
  // Parse the date string into a Date object
  const timestamp = new Date(dateString);

  // Check for invalid date
  if (isNaN(timestamp.getTime())) {
    throw new Error("Invalid date string provided.");
  }

  // Get the current time
  const now = new Date();

  // Calculate the difference in milliseconds
  const timeDifference = now.getTime() - timestamp.getTime();

  // Convert time difference to minutes and hours
  const minutesAgo = Math.floor(timeDifference / (1000 * 60));
  const hoursAgo = Math.floor(minutesAgo / 60);

  // Format the date into a readable format e.g. "November 27"
  const options: Intl.DateTimeFormatOptions = { month: "long", day: "numeric" };
  const formattedDate = timestamp.toLocaleDateString(undefined, options);

  // Determine the time difference string
  let timeAgoStr: string;
  if (minutesAgo < 1) {
    timeAgoStr = "just now";
  } else if (minutesAgo < 60) {
    // Less than an hour ago, display minutes
    timeAgoStr = `${minutesAgo} ${minutesAgo === 1 ? "minute" : "minutes"} ago`;
  } else if (hoursAgo < 24) {
    // Less than a day ago, display hours
    timeAgoStr = `${hoursAgo} ${hoursAgo === 1 ? "hour" : "hours"} ago`;
  } else {
    // More than a day ago, display the formatted date
    timeAgoStr = formattedDate;
  }

  // Return the final readable string
  return timeAgoStr;
};

export const examplePrompts = [
  {
    title: "Stock Price",
    prompt:
      "Plot a chart of NVDA and TESLA stock price for 2023. Save the result to a file named nvda_tesla.png",
  },
  {
    title: "Sine Wave",
    prompt:
      "Write a python script to plot a sine wave and save it to disc as a png file sine_wave.png",
  },
  {
    title: "Markdown",
    prompt:
      "List out the top 5 rivers in africa and their length and return that as a markdown table. Do not try to write any code, just write the table",
  },
  {
    title: "Paint",
    prompt:
      "paint a picture of a glass of ethiopian coffee, freshly brewed in a tall glass cup, on a table right in front of a lush green forest scenery",
  },
];

/**
 * Recursively sanitizes JSON objects by replacing specific keys with a given value.
 * @param {JsonValue} data - The JSON data to be sanitized.
 * @param {string[]} keys - An array of keys to be replaced in the JSON object.
 * @param {string} replacement - The value to use as replacement for the specified keys.
 * @returns {JsonValue} - The sanitized JSON data.
 */
export const sanitizeConfig = (
  data: any,
  keys: string[] = ["api_key"],
  replacement: string = "********"
): any => {
  if (Array.isArray(data)) {
    return data.map((item) => sanitizeConfig(item, keys, replacement));
  } else if (typeof data === "object" && data !== null) {
    Object.keys(data).forEach((key) => {
      if (keys.includes(key)) {
        data[key] = replacement;
      } else {
        data[key] = sanitizeConfig(data[key], keys, replacement);
      }
    });
  }
  return data;
};
