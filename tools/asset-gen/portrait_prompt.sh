#!/usr/bin/env bash
# usage: portrait_prompt.sh <age> <health> <body>  -> prints the fixed-template prompt
age=$1; health=$2; body=$3
case $age in
  kitten) A="a kitten: small body, big round head, short legs, rounder proportions";;
  young) A="a young adolescent cat: slimmer, slightly smaller than a full adult, longer legs than a kitten";;
  adult) A="a full-grown adult cat";;
esac
case $health in
  healthy) H="calm friendly expression, bright eyes, ears up, smooth fur";;
  sick) H="tired expression, half-lidded dull eyes, ears drooping, slightly rough fur, slightly slumped shoulders";;
  bedridden) H="lying down flat on its belly with the head resting on the front paws, eyes nearly closed, very weak and tired, ears drooping, slightly rough fur";;
  delinquent) H="mischievous scruffy look, narrowed sly eyes, ears slightly back, a small smirk, slightly messy fur";;
esac
case $body in
  normal) B="normal body shape";;
  chubby) B="very chubby: a clearly round, pear-shaped heavy body about 40 percent wider than a normal cat, big bulging soft belly, thick short legs, fuller cheeks";;
esac
echo "Draw exactly the same cat as the reference image (identical markings: black head with white blaze and white muzzle, white chest and belly, two large black body patches, black tail, white paws, yellow eyes, identical flat cel style and line weight), but as $A. $H. $B. Keep the same seated three-quarter pose with the tail and body patches visible and both front paws visible (except when lying down). Full body, centered, generous empty margin, transparent background, no text, no shadow."
