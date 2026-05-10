import React from "react";
import { Composition } from "remotion";
import { ProjectVideo } from "./ProjectVideo";
import { FPS, TOTAL_FRAMES } from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/*
        Primary cut — vertical 9:16 for X (Twitter), LinkedIn mobile feed,
        Reels, Shorts, TikTok. This is the one to publish first.
      */}
      <Composition
        id="DonjonVertical"
        component={ProjectVideo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
      />

      {/*
        Bonus cut — square 1:1 for LinkedIn desktop feed, Instagram feed,
        and X desktop. Same composition, different canvas.
      */}
      <Composition
        id="DonjonSquare"
        component={ProjectVideo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1080}
      />
    </>
  );
};
